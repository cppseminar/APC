// go get github.com/xeipuuv/gojsonschema

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/filters"
	"github.com/docker/docker/client"
	"github.com/docker/docker/pkg/stdcopy"
	"github.com/xeipuuv/gojsonschema"
)

type dockerConfig struct {
	// File path to folder mounted as /source (should contain source files)
	volume dockerVolume
	// Name of docker image, that will be run
	dockerImage string
}

type dockerVolume struct {
	dirPath string
	volume  string
	rmDir   bool
}

func (volume dockerVolume) Cleanup() {
	if volume.rmDir {
		panic("Not implemented tmp folder deletion")
	}

	d, err := os.Open(volume.dirPath)
	if err != nil {
		return
	}
	defer d.Close()
	names, err := d.Readdirnames(-1)
	if err != nil {
		return
	}
	for _, name := range names {
		err = os.RemoveAll(filepath.Join(volume.dirPath, name))
	}
}

type requestMessage struct {
	ReturnURL   string
	DockerImage string
	Files       map[string]string
	MaxRunTime  int
}

var schema *gojsonschema.Schema

var queue = make(chan requestMessage, 100)

const schemaStr = `
{
	"$schema": "http://json-schema.org/draft-07/schema",
	"$id": "http://example.com/example.json",
	"type": "object",
	"title": "The root schema",
	"description": "The root schema comprises the entire JSON document.",
	"default": {},
	"required": [
		"returnUrl",
		"dockerImage",
		"files",
		"maxRunTime"
	],
	"properties": {
		"returnUrl": {
			"$id": "#/properties/returnUrl",
			"type": "string",
			"format": "uri",
			"title": "The returnUrl schema",
			"description": "Result of the run will be submited to this URL."
		},
		"dockerImage": {
			"$id": "#/properties/dockerImage",
			"type": "string",
			"title": "Name of the docker image",
			"description": "The image will be used to process the files and collect results."
		},
		"files": {
			"$id": "#/properties/files",
			"type": "object",
			"title": "The files schema",
			"description": "An explanation about the purpose of this instance.",
			"minProperties": 1,
			"maxProperties": 10,
			"patternProperties": {
			  "^[A-Za-z0-9_\\-\\.]{4,250}$": {
				  "type": "string",
				  "minLength": 1,
				  "maxLength": 102400
			  }
			},
			"examples": [
				{
					"main.cpp": "#include <iostream>\n\nint main() { std::cout << \"Hello json!\"; }"
				}
			],
			"additionalProperties": false
		},
		"maxRunTime": {
			"$id": "#/properties/maxRunTime",
			"type": "number",
			"title": "Maximum runnig time",
			"description": "After this many seconds the test will break.",
			"multipleOf": 1.0,
			"minimum": 1,
			"maximum": 900
		}
	},
	"additionalProperties": false
  }`

func waitExit(ctx context.Context, dockerCli *client.Client, containerID string) <-chan int {
	if len(containerID) == 0 {
		// containerID can never be empty
		panic("Internal Error: waitExit needs a containerID as parameter")
	}

	// WaitConditionNextExit is used to wait for the next time the state changes
	// to a non-running state. If the state is currently "created" or "exited",
	// this would cause Wait() to block until either the container runs and exits
	// or is removed.
	resultC, errC := dockerCli.ContainerWait(ctx, containerID, container.WaitConditionNextExit)

	statusC := make(chan int)
	go func() {
		select {
		case result := <-resultC:
			if result.Error != nil {
				statusC <- 125
			} else {
				statusC <- int(result.StatusCode)
			}
		case <-errC:
			log.Println("Error in attach to container")
			statusC <- 125
		}
	}()

	return statusC
}

func formatVolume(volume dockerVolume) string {
	if volume.volume != "" {
		return volume.volume + `:/sources`
	}
	return volume.dirPath + `:/sources`
}

func dockerExec(config dockerConfig) (string, error) {
	var errorMessage = errors.New("Error occured tests were not executed")

	formattedVolume := formatVolume(config.volume)

	// TODO: Context should be cancellable, for docker timeout
	ctx := context.Background()
	cli, err := client.NewEnvClient()

	if err != nil {
		log.Printf("Error while creating docker client: %v", err)
		return "", errorMessage
	}

	var dockerContainerConfig = &container.Config{Image: config.dockerImage}
	var dockerHostConfig = &container.HostConfig{Binds: []string{formattedVolume}}

	container, err := cli.ContainerCreate(ctx, dockerContainerConfig, dockerHostConfig, nil, "")
	if err != nil {
		log.Printf("Error while creating docker image (%v): %v",
			config.dockerImage, err)
		return "", errorMessage
	}
	var containerWaitC = waitExit(ctx, cli, container.ID)

	// This should delete all not running containers
	defer cli.ContainersPrune(ctx, filters.Args{})

	response, err := cli.ContainerAttach(ctx, container.ID,
		types.ContainerAttachOptions{
			Stdout: true,
			Stream: true,
			Stderr: true,
		})

	if err != nil {
		log.Printf("Error on docker attach: %v", err)
		return "", errorMessage
	}

	err = cli.ContainerStart(ctx, container.ID, types.ContainerStartOptions{})

	if err != nil {
		log.Printf("Error on docker image (%v) start: %v", config.dockerImage, err)
		return "", errorMessage
	}
	// Wait for container to finish
	<-containerWaitC
	stdout, stderr := strings.Builder{}, strings.Builder{}
	stdcopy.StdCopy(&stdout, &stderr, response.Reader)
	return stdout.String(), nil
}

// Determine if this run should use volumes, instead of direct tmp paths
// For using volumes there are 2 preconditions:
//  1. Env variable must be set, with name of docker volume
//  2. Directory /volume should be created
func getVolume() dockerVolume {
	const dirPath = "/volume"
	var envVolume = os.Getenv("VOLUME_NAME")
	var volumeExists bool = func(dirName string) bool {
		// TODO: There is not check, if directory is actually writable
		volumeInfo, err := os.Stat(dirName)
		if err != nil {
			return false
		}
		return volumeInfo.IsDir()
	}(dirPath)

	if envVolume == "" || !volumeExists {
		// Create tmp folder
		log.Println(envVolume, volumeExists)
		panic("Not implemented tmp folder mapping :(")
	}

	// We are in docker environment
	return dockerVolume{
		dirPath: dirPath,
		volume:  envVolume,
		rmDir:   false,
	}
}

func getSchema() *gojsonschema.Schema {
	schemaLoader := gojsonschema.NewStringLoader(schemaStr)

	schema, err := gojsonschema.NewSchema(schemaLoader)
	if err != nil {
		log.Fatal(err)
	}

	return schema
}

func processMessages() {
	for {
		msg := <-queue

		log.Printf("%+v\n", msg)

		func() {
			var volume = getVolume()
			var dir = volume.dirPath

			defer volume.Cleanup()

			for file, content := range msg.Files {
				path := filepath.Join(dir, file)

				err := ioutil.WriteFile(path, []byte(content), 0644)
				if err != nil {
					log.Println(err)
					return
				}
			}

			log.Println("Docker exec is starting")
			var config = dockerConfig{
				volume:      volume,
				dockerImage: msg.DockerImage,
			}
			result, err := dockerExec(config)
			log.Println("Docker exec finished")

			if err != nil {
				log.Println("Error occured during dockerExec")
				// Let's send error as output. This should be replaced by
				// template string
				result = err.Error()
			}

			var jsonStr = []byte(`{"description":"` + result + `"}`)
			req, err := http.NewRequest("PATCH", "http://output-proxy:10018", bytes.NewBuffer(jsonStr))
			if err != nil {
				log.Println("Cannot create request", err)
			}
			req.Header.Set("X-Send-To", msg.ReturnURL)
			req.Header.Set("Content-type", "application/json")

			resp, err := httpClient.Do(req)
			if err != nil {
				log.Println("Cannot forward request", err)
				return
			}
			if resp.StatusCode < 200 || resp.StatusCode >= 300 {
				log.Println("Forward request failed", resp)
			}
		}()
	}
}

var tr = &http.Transport{
	ResponseHeaderTimeout:  10 * time.Second,
	IdleConnTimeout:        30 * time.Second,
	MaxResponseHeaderBytes: 1024,
}

var httpClient = &http.Client{Transport: tr}

func main() {
	log.Println("Queue is starting")
	schema = getSchema()

	srv := &http.Server{
		Addr:         ":10009",
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
		Handler:      http.HandlerFunc(ServerHandler),
	}

	// start process messages queue
	go processMessages()

	err := srv.ListenAndServe()
	if err != nil {
		log.Fatal(err) // we cannot run the server this, is fatal
	}
}

func processRequest(r *http.Request) int {
	if r.Method != "POST" {
		return http.StatusBadRequest
	}

	req, err := ioutil.ReadAll(r.Body)
	if err != nil {
		return http.StatusInternalServerError
	}

	// check payload against json scheme to validate it
	jsonDocument := gojsonschema.NewBytesLoader(req)

	result, err := schema.Validate(jsonDocument)
	if err != nil {
		log.Println(err)
		return http.StatusBadRequest
	}

	if !result.Valid() {
		log.Println(result.Errors())
		return http.StatusBadRequest
	}

	// so here the request is validated, we are good to go and create new message
	var msg requestMessage
	if err := json.Unmarshal(req, &msg); err != nil {
		log.Println(err)
		return http.StatusBadRequest
	}

	select {
	case queue <- msg: // normally just add it
	default: // we are full
		log.Println("Queue is full")
		return http.StatusTooManyRequests
	}

	return http.StatusOK
}

func ServerHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(processRequest(r))
}
