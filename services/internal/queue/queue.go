package queue

import (
	"archive/zip"
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"services/internal/queue/docker"

	"github.com/xeipuuv/gojsonschema"
	"golang.org/x/sys/unix"
)

type requestMessage struct {
	ReturnURL   string
	DockerImage string
	Files       map[string]string
	MaxRunTime  int         // in seconds
	Memory      int         // in megabytes
	MetaData    interface{} // pass this along
}

var schema *gojsonschema.Schema

var queue = make(chan requestMessage, 100)

const schemaStr = `
{
	"$schema": "http://json-schema.org/draft-07/schema",
	"$id": "http://example.com/example.json",
	"type": "object",
	"title": "The root schema",
	"default": {},
	"required": [
		"returnUrl",
		"dockerImage",
		"files"
	],
	"properties": {
		"metaData": {
			"$id": "#/properties/metaData",
			"type": "object",
			"title": "Metadata of request",
			"description": "Metadata passed back to returnUrl."
		},
		"returnUrl": {
			"$id": "#/properties/returnUrl",
			"type": "string",
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
			"minProperties": 1,
			"maxProperties": 10,
			"patternProperties": {
			  "^[A-Za-z0-9_\\-\\.]{4,250}$": {
				  "type": "string",
				  "minLength": 1,
				  "maxLength": 512000
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
			"title": "Maximum running time of docker image",
			"description": "After this many seconds the test will break.",
			"multipleOf": 1.0,
			"minimum": 1,
			"maximum": 1800
		},
		"memory": {
			"$id": "#/properties/memory",
			"type": "number",
			"title": "Maximum memory available to the docker",
			"description": "In MB of memory.",
			"multipleOf": 1.0,
			"minimum": 10
		}
	},
	"additionalProperties": false
  }`

func getSchema() *gojsonschema.Schema {
	schemaLoader := gojsonschema.NewStringLoader(schemaStr)

	schema, err := gojsonschema.NewSchema(schemaLoader)
	if err != nil {
		log.Panicln("Cannot load json schema ", err)
	}

	return schema
}

func getVolume(guestPath string, readOnly bool) docker.DockerVolume {
	path, err := ioutil.TempDir("", "dockerVolume")
	if err != nil {
		log.Panicln("Cannot create tmp folder", err)
	}

	return docker.DockerVolume{
		HostPath:  path,
		GuestPath: guestPath,
		ReadOnly:  readOnly,
	}
}

func readJsonData(path string) (map[string]interface{}, error) {
	jsonFile, err := os.Open(path)
	if err != nil {
		log.Println(err)
		return nil, err
	}
	// defer the closing of our jsonFile so that we can parse it later on
	defer jsonFile.Close()

	byteValue, _ := ioutil.ReadAll(jsonFile)

	var result map[string]interface{}
	json.Unmarshal([]byte(byteValue), &result)

	return result, nil
}

func zipOutputToBase64(output_path string) (string, error) {
	output_path, err := filepath.Abs(output_path)
	if err != nil {
		log.Printf("Cannot resolve absolute form of output_path (%s)\n", output_path)
		log.Println(err)
		return "", err
	}

	f, err := ioutil.TempFile("", "output*")
	if err != nil {
		log.Println(err)
		return "", err
	}

	defer os.Remove(f.Name())

	err = func() error {
		defer f.Close()

		zipWriter := zip.NewWriter(f)
		defer zipWriter.Close()

		walker := func(path string, info os.FileInfo, err error) error {
			if err != nil {
				log.Println(err)
				return err
			}
			if info.IsDir() {
				return nil
			}
			file, err := os.Open(path)
			if err != nil {
				log.Println(err)
				return err
			}
			defer file.Close()

			// make the path relative, so zip will display it nicely
			if !strings.HasPrefix(path, output_path) {
				log.Panicf("We make sure output_path (%s) is absolute, but path (%s) is not prefix.", output_path, path)
			}

			path = strings.TrimPrefix(path, output_path)
			path = strings.TrimLeft(path, "/") // make it relative

			f, err := zipWriter.Create(path)
			if err != nil {
				log.Println(err)
				return err
			}

			_, err = io.Copy(f, file)
			if err != nil {
				log.Println(err)
				return err
			}

			return nil
		}
		err = filepath.Walk(output_path, walker)
		if err != nil {
			return err
		}

		return nil
	}()

	if err != nil {
		return "", err
	}

	data, err := ioutil.ReadFile(f.Name())
	if err != nil {
		log.Println(err)
		return "", err
	}

	return base64.StdEncoding.EncodeToString(data), nil
}

func processMessages(wg *sync.WaitGroup) {
	defer wg.Done() // let main know we are done cleaning up

	for {
		msg, more := <-queue
		if !more {
			log.Println("Message queue empty and closed.")
			return
		}

		log.Println("Start processing of message.")

		func() {
			// This is to always log last request, in case something went terribly bad
			defer func() {
				r := recover()
				if r != nil {
					log.Printf("Panicing on message %v\n", msg)
					panic(r) // just fail quickly
				} else {
					log.Println("Finished processing of message.")
				}
			}()

			var outputVolume docker.DockerVolume
			defer outputVolume.Cleanup()

			result := func() string {
				env, err := docker.GetDockerEnv(msg.DockerImage)
				if err != nil {
					return err.Error()
				}

				outputVolume = getVolume(strings.TrimSpace(env["OUTPUT_PATH"]), false)

				submissionVolume := getVolume(strings.TrimSpace(env["SUBMISSION_PATH"]), true)
				defer submissionVolume.Cleanup()

				for file, content := range msg.Files {
					path := filepath.Join(submissionVolume.HostPath, file)

					err := ioutil.WriteFile(path, []byte(content), 0644)
					if err != nil {
						log.Println(err)
						return err.Error()
					}
				}

				config := docker.DockerConfig{
					Volumes:     []docker.DockerVolume{outputVolume, submissionVolume},
					DockerImage: msg.DockerImage,
					Timeout:     uint16(msg.MaxRunTime),
					Memory:      int64(msg.Memory * 1024 * 1024),
					Username:    arguments.DockerUsername,
					Password:    arguments.DockerPassword,
				}

				result, err := docker.DockerExec(config)

				if err != nil {
					// There will be some logs already, so just log request json
					log.Printf("Error while running docker image on message %+v\n", msg)
					return err.Error()
				}

				return result
			}()

			// this is path for output from our container (very not standard, but whatever)
			outputPath := outputVolume.HostPath

			// save whole message there so it will be available in the zip file
			msgJson, err := json.MarshalIndent(msg, "", " ")
			if err != nil {
				log.Println("Cannot save msg to json", err)
				msgJson = []byte(err.Error())
			}

			tmp, err := ioutil.TempFile(outputPath, "__msg__*.json")
			if err == nil {
				_, err = tmp.Write(msgJson)
			}

			if err != nil {
				log.Println("Cannot write json", err)
			}

			output := map[string]interface{}{"result": result}

			if outputPath != "" {
				data, err := readJsonData(filepath.Join(outputPath, "students.json"))
				if err != nil {
					output["students"] = err.Error()
				} else {
					output["students"] = data
				}

				data, err = readJsonData(filepath.Join(outputPath, "teachers.json"))
				if err != nil {
					output["teachers"] = err.Error()
				} else {
					output["teachers"] = data
				}
			}

			zipdata, err := zipOutputToBase64(outputPath)
			if err != nil {
				output["data"] = err
			} else {
				output["data"] = zipdata
			}

			// copy meta from input
			output["metaData"] = msg.MetaData

			body, err := json.Marshal(output)
			if err != nil {
				log.Println("Cannot create json", err)
				return
			}

			req, err := http.NewRequest("POST", "http://"+strings.TrimRight(msg.ReturnURL, "/")+"/results", bytes.NewBuffer(body))
			if err != nil {
				log.Println("Cannot create request", err)
				return
			}

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

func processTestRequestInternal(r *http.Request) int {
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
	msg := requestMessage{
		MaxRunTime: 300,
		Memory:     2048,
	}
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

func serverHandler(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path == "/test" && r.Method == "POST" {
		w.WriteHeader(processTestRequestInternal(r))
	} else {
		log.Printf("Unsupported request %v %v ip %v", r.Method, r.URL.Path, r.RemoteAddr)
		w.WriteHeader(http.StatusNotFound)
	}
}

func startHttpServer(wg *sync.WaitGroup, serverURL string) *http.Server {
	srv := &http.Server{
		Addr:         serverURL,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
		Handler:      http.HandlerFunc(serverHandler),
	}

	go func() {
		defer wg.Done() // let main know we are done cleaning up

		// always returns error. ErrServerClosed on graceful close
		if err := srv.ListenAndServe(); err != http.ErrServerClosed {
			log.Fatalf("Listen and serve failed with: %v\n", err)
		} else {
			log.Println("Server stopped gracefully...")
		}
	}()

	return srv
}

func Run(ctx context.Context, out io.Writer) int {
	log.SetOutput(out)

	signalChan := make(chan os.Signal, 1)
	signal.Notify(signalChan, os.Interrupt, unix.SIGTERM)
	defer signal.Stop(signalChan)

	log.Println("Queued is starting.")

	defer func() {
		r := recover()
		if r != nil {
			log.Printf("Panicing %v\n", r)
			panic(r)
		}
	}()

	args := GetArguments()

	schema = getSchema()

	serverURL := fmt.Sprintf("%v:%v", args.ServerHost, args.ServerPort)

	exitDone := &sync.WaitGroup{}
	exitDone.Add(2) // we are waiting for http server and our process message queue

	// start process messages queue
	go processMessages(exitDone)

	log.Println("Starting http server on", serverURL, "...")

	srv := startHttpServer(exitDone, serverURL)

	<-signalChan // wait for signal
	log.Printf("Got SIGINT/SIGTERM, exiting...")

	// using 10 as timeout so http server has some time to quit
	func() {
		ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
		defer cancel()

		if err := srv.Shutdown(ctx); err != nil {
			log.Println("Cannot shutdown server", err)
			os.Exit(1)
		}
	}()

	close(queue) // exit the main loop

	// wait for goroutine started in startHttpServer() to stop
	exitDone.Wait()

	log.Println("Queued has ended.")

	return 0
}
