// go get github.com/xeipuuv/gojsonschema

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
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
	mountPoint string
	// Name of docker image, that will be run
	dockerImage string
}

type RequestMessage struct {
	ReturnUrl   string
	DockerImage string
	Files       map[string]string
	MaxRunTime  int
}

var schema *gojsonschema.Schema

var queue = make(chan RequestMessage, 100)

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
			panic("Error attach")
			// statusC <- 125
		}
	}()

	return statusC
}

func formatVolume(folderPath string) (string, error) {
	absolutePath, err := filepath.Abs(folderPath)
	if err != nil {
		return "", fmt.Errorf("Wrong file path %v", folderPath)
	}
	return absolutePath + `:/sources`, nil
}

func DockerExec(config dockerConfig) (string, error) {
	var errorMessage = errors.New("Error occured tests were not executed")

	volume, err := formatVolume(config.mountPoint)

	if err != nil {
		log.Printf("Error in path manipulation (%v): %v", config.mountPoint, err)
		return "", errorMessage
	}

	// TODO: Context should be cancellable, for docker timeout
	ctx := context.Background()
	cli, err := client.NewEnvClient()

	if err != nil {
		log.Printf("Error while creating docker client: %v", err)
		return "", errorMessage
	}

	container, err := cli.ContainerCreate(ctx, &container.Config{
		Image: config.dockerImage,
	}, &container.HostConfig{
		Binds: []string{volume}}, nil, "")
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
			dir, err := ioutil.TempDir("", "queue-go")
			if err != nil {
				log.Println(err)
				return
			}

			defer func() {
				if err := os.RemoveAll(dir); err != nil {
					log.Println(err)
				}
			}()

			for file, content := range msg.Files {
				path := filepath.Join(dir, file)

				err := ioutil.WriteFile(path, []byte(content), 0644)
				if err != nil {
					log.Println(err)
					return
				}
			}

			log.Println("Detailed log of incoming request")
			var config = dockerConfig{
				mountPoint:  dir,
				dockerImage: msg.DockerImage,
			}
			result, err := DockerExec(config)

			if err != nil {
				log.Println("Error occured during DockerExec")
				// Let's send error as output. This should be replaced by
				// template string
				result = err.Error()
			}

			var jsonStr = []byte(`{"description":"` + result + `"}`)
			req, err := http.NewRequest("PATCH", "http://localhost:10018", bytes.NewBuffer(jsonStr))
			if err != nil {
				log.Println("Cannot create request", err)
			}
			req.Header.Set("X-Send-To", msg.ReturnUrl)
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
	var msg RequestMessage
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
