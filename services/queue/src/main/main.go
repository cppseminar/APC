package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"services/queue/docker"

	"github.com/xeipuuv/gojsonschema"
)

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

// Determine if this run should use volumes, instead of direct tmp paths
// For using volumes there are 2 preconditions:
//  1. Env variable must be set, with name of docker volume
//  2. Directory /volume should be created
func getVolume() docker.DockerVolume {
	const dirPath = "/volume" // We assume volume location here. This should
	// Only be the case, if  we are running in docker container.  You are free
	// to change this via environment variable or smth else. But check compose
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
	return docker.DockerVolume{
		DirPath: dirPath,
		Volume:  envVolume,
		RmDir:   false,
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
			var dir = volume.DirPath

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
			var config = docker.DockerConfig{
				Volume:      volume,
				DockerImage: msg.DockerImage,
			}
			result, err := docker.DockerExec(config)
			log.Println("Docker exec finished")

			if err != nil {
				log.Println("Error occured during dockerExec")
				// Let's send error as output. This should be replaced by
				// template string
				result = err.Error()
			}

			body, err := json.Marshal(map[string]string{"description": result})
			if err != nil {
				log.Println("Cannot create json", err)
				return
			}

			req, err := http.NewRequest("PATCH", "http://output-proxy:10018", bytes.NewBuffer(body))
			if err != nil {
				log.Println("Cannot create request", err)
				return
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
				return
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

func logInit() {
	log.Println("Queue is starting")
	volume := getVolume()
	// This volume logging is important, or else there would be hard to explain
	// errors inside other docker containers.
	if volume.Volume == "" {
		log.Println("Volumes not configured, using tmp folders")
	} else {
		log.Printf("Using volume mapping: %v\n", volume.Volume)
	}
	volume.Cleanup()
}

func main() {
	logInit() // Print init info
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
