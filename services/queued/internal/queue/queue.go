package queue

import (
	"archive/zip"
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
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
		log.Panicln("<3>Cannot load json schema ", err)
	}

	return schema
}

func getVolume(guestPath string, readOnly bool) docker.DockerVolume {
	path, err := os.MkdirTemp(os.Getenv("SHARED_DATA_DIR"), "dockerVolume")
	if err != nil {
		log.Panicln("<3>Cannot create tmp folder", err)
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
		log.Println("<3>Error opening path with json", err)
		return nil, err
	}
	// defer the closing of our jsonFile so that we can parse it later on
	defer jsonFile.Close()

	byteValue, _ := io.ReadAll(jsonFile)

	var result map[string]interface{}
	err = json.Unmarshal([]byte(byteValue), &result)

	return result, err
}

func writeJsonData(file *os.File, data any) error {
	jsonData, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		log.Println("<3>Cannot format json", err)
		return err
	}

	_, err = file.Write(jsonData)
	if err != nil {
		log.Println("<3>Cannot write json", err)
		return err
	}

	return nil
}

func writeJsonDataToTemp(path string, pattern string, data any) (string, error) {
	tmp, err := os.CreateTemp(path, pattern)
	if err != nil {
		log.Println("<3>Cannot create temp file", err)
		return "", err
	}

	defer tmp.Close()

	err = writeJsonData(tmp, data)
	if err != nil {
		os.Remove(tmp.Name())
		return "", err
	}

	return tmp.Name(), nil
}

func zipOutputToBase64(output_path string) (string, error) {
	output_path, err := filepath.Abs(output_path)
	if err != nil {
		log.Printf("<3>Cannot resolve absolute form of output_path (%s) %v\n", output_path, err)
		return "", err
	}

	f, err := os.CreateTemp("", "output*")
	if err != nil {
		log.Println("<3>Cannot create temp file", err)
		return "", err
	}

	defer os.Remove(f.Name())

	err = func() error {
		defer f.Close()

		zipWriter := zip.NewWriter(f)
		defer zipWriter.Close()

		walker := func(path string, info os.FileInfo, err error) error {
			if err != nil {
				log.Println("<3>Error while walking path", err)
				return err
			}
			if info.IsDir() {
				return nil
			}
			file, err := os.Open(path)
			if err != nil {
				log.Println("<3>Cannot open file", err)
				return err
			}
			defer file.Close()

			// make the path relative, so zip will display it nicely
			if !strings.HasPrefix(path, output_path) {
				log.Panicf("<3>We make sure output_path (%s) is absolute, but path (%s) is not prefix.", output_path, path)
			}

			path = strings.TrimPrefix(path, output_path)
			path = strings.TrimLeft(path, "/") // make it relative

			f, err := zipWriter.Create(path)
			if err != nil {
				log.Println("<3>Cannot create zip writer", err)
				return err
			}

			_, err = io.Copy(f, file)
			if err != nil {
				log.Println("<3>File copy failed", err)
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

	data, err := os.ReadFile(f.Name())
	if err != nil {
		log.Println("<3>Reading of file failed", err)
		return "", err
	}

	return base64.StdEncoding.EncodeToString(data), nil
}

func processMessages(wg *sync.WaitGroup) {
	defer wg.Done() // let main know we are done cleaning up

	for {
		msg, more := <-queue
		if !more {
			log.Println("<6>Message queue empty and closed.")
			return
		}

		log.Println("<6>Start processing of message.")

		func() {
			// This is to always log last request, in case something went terribly bad
			defer func() {
				r := recover()
				if r != nil {
					log.Panicf("<3>Panicing on message %v", msg.MetaData) // just fail quickly
				} else {
					log.Println("<6>Finished processing of message.")
				}
			}()

			var outputVolume docker.DockerVolume
			// we do not want to delte the tmp files, it may be useful,
			// also the line below will not do the trick, since args
			// are bound when defer is called, not when the function is
			// called, so it will call Cleanup on empty path :(
			//defer outputVolume.Cleanup()

			result, err := func() (string, error) {
				ctx := context.Background()

				config := docker.DockerConfig{
					Volumes:     []docker.DockerVolume{},
					DockerImage: msg.DockerImage,
					Timeout:     uint16(msg.MaxRunTime),
					Memory:      int64(msg.Memory * 1024 * 1024),
					Username:    arguments.DockerUsername,
					Password:    arguments.DockerPassword,
				}

				docker.PullImage(ctx, config)

				env, err := docker.GetDockerEnv(ctx, msg.DockerImage)
				if err != nil {
					return "", err
				}

				outputVolume = getVolume(strings.TrimSpace(env["OUTPUT_PATH"]), false)

				submissionVolume := getVolume(strings.TrimSpace(env["SUBMISSION_PATH"]), true)
				defer submissionVolume.Cleanup()

				for file, content := range msg.Files {
					path := filepath.Join(submissionVolume.HostPath, file)

					err := os.WriteFile(path, []byte(content), 0644)
					if err != nil {
						log.Println("<3>Cannot write submission file", err)
						return "", err
					}
				}

				config.Volumes = append(config.Volumes, outputVolume, submissionVolume)

				result, err := docker.DockerExec(ctx, config)

				if err != nil {
					// There will be some logs already, so just log request json
					msgJson, errJson := json.Marshal(msg)
					if errJson != nil {
						// we are deeply screwed...
						log.Panicln("<3>Cannot format message as json!", errJson)
					}

					log.Println("<3>Error while running docker image on message", string(msgJson))
					return "", err
				}

				return result, nil
			}()

			// error may be replaced later, se we always get the last
			// error, but it seems to be OK, since we get the info
			// that something is wrong
			output := map[string]interface{}{
				"result": result,
				"error":  func() any { if err != nil { return err.Error() }; return nil }(),
			}

			// this is path for output from our container (very not standard, but whatever)
			outputPath := outputVolume.HostPath

			// save whole message there so it will be available in the zip file
			path, err := writeJsonDataToTemp(outputPath, "__msg__*.json", msg)
			if err != nil {
				log.Println("<4>Cannot save input msg to file", err)

				// let try at least something
				msg := map[string]any{
					"status": "cannot save input msg",
					"error":  err.Error(),
				}

				path, err := writeJsonDataToTemp(outputPath, "__msg__*.json", msg)
				if err != nil {
					log.Println("<4>Cannot save error msg to file", err)
				} else {
					defer os.Remove(path)
				}
			} else {
				defer os.Remove(path)
			}

			if outputPath != "" {
				data, err := readJsonData(filepath.Join(outputPath, "students.json"))
				if err != nil {
					log.Println("<4>Cannot read students.json", err)
					output["error"] = fmt.Sprintf("Cannot read students.json %v", err)
				} else {
					output["students"] = data
				}

				data, err = readJsonData(filepath.Join(outputPath, "teachers.json"))
				if err != nil {
					log.Println("<4>Cannot read teachers.json", err)
					output["error"] = fmt.Sprintf("Cannot read teachers.json %v", err)
				} else {
					output["teachers"] = data
				}

				zipdata, err := zipOutputToBase64(outputPath)
				if err != nil {
					log.Println("<4>Cannot create output zip", err)
					output["error"] = fmt.Sprintf("Cannot create output zip %v", err)
				} else {
					output["data"] = zipdata
				}
			}

			// copy meta from input
			output["metaData"] = msg.MetaData

			body, err := json.Marshal(output)
			if err != nil {
				log.Println("<3>Cannot create json", err)
				return
			}

			req, err := http.NewRequest("POST", "http://"+strings.TrimRight(msg.ReturnURL, "/")+"/results", bytes.NewBuffer(body))
			if err != nil {
				log.Println("<3>Cannot create request", err)
				return
			}

			req.Header.Set("Content-type", "application/json")

			resp, err := httpClient.Do(req)
			if err != nil {
				log.Println("<3>Cannot forward request", err)
				return
			}

			resp.Body.Close() // no need to defer this

			if resp.StatusCode < 200 || resp.StatusCode >= 300 {
				log.Println("<3>Forward request failed", resp)
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
	req, err := io.ReadAll(r.Body)
	if err != nil {
		return http.StatusInternalServerError
	}

	// check payload against json scheme to validate it
	jsonDocument := gojsonschema.NewBytesLoader(req)

	result, err := schema.Validate(jsonDocument)
	if err != nil {
		log.Println("<3>Cannot validate json against schema", err)
		return http.StatusBadRequest
	}

	if !result.Valid() {
		log.Println("<3>Json schema validation failed", result.Errors())
		return http.StatusBadRequest
	}

	// so here the request is validated, we are good to go and create new message
	msg := requestMessage{
		MaxRunTime: 500, // 300 for test and 200 for build
		Memory:     2048,
	}
	if err := json.Unmarshal(req, &msg); err != nil {
		log.Println("<3>Cannot parse json", err)
		return http.StatusBadRequest
	}

	select {
	case queue <- msg: // normally just add it
	default: // we are full
		log.Println("<3>Queue is full")
		return http.StatusTooManyRequests
	}

	return http.StatusOK
}

func serverHandler(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path == "/test" && r.Method == "POST" {
		w.WriteHeader(processTestRequestInternal(r))
	} else {
		log.Printf("<3>Unsupported request %v %v ip %v\n", r.Method, r.URL.Path, r.RemoteAddr)
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
			log.Fatalf("<3>Listen and serve failed with: %v\n", err)
		} else {
			log.Println("<6>Server stopped gracefully...")
		}
	}()

	return srv
}

func Run(ctx context.Context, out io.Writer) int {
	log.SetOutput(out)
	log.SetFlags(0)

	signalChan := make(chan os.Signal, 1)
	signal.Notify(signalChan, os.Interrupt, unix.SIGTERM)
	defer signal.Stop(signalChan)

	log.Println("<6>Queued is starting.")

	defer func() {
		r := recover()
		if r != nil {
			log.Panicln("<3>Panicing", r)
		}
	}()

	args := GetArguments()

	schema = getSchema()

	serverURL := fmt.Sprintf("%v:%v", args.ServerHost, args.ServerPort)

	exitDone := &sync.WaitGroup{}
	exitDone.Add(2) // we are waiting for http server and our process message queue

	// start process messages queue
	go processMessages(exitDone)

	log.Println("<6>Starting http server on", serverURL, "...")

	srv := startHttpServer(exitDone, serverURL)

	<-signalChan // wait for signal
	log.Printf("<6>Got SIGINT/SIGTERM, exiting...\n")

	// using 10 as timeout so http server has some time to quit
	func() {
		ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
		defer cancel()

		if err := srv.Shutdown(ctx); err != nil {
			log.Println("<4>Cannot shutdown server", err)
			os.Exit(1)
		}
	}()

	close(queue) // exit the main loop

	// wait for goroutine started in startHttpServer() to stop
	exitDone.Wait()

	log.Println("<6>Queued has ended.")

	return 0
}
