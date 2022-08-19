package queue

import (
	"archive/zip"
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
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

var tr = &http.Transport{
	ResponseHeaderTimeout:  10 * time.Second,
	IdleConnTimeout:        30 * time.Second,
	MaxResponseHeaderBytes: 1024,
}

var httpClient = &http.Client{Transport: tr}

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
	path, err := ioutil.TempDir("", "dockerVolume")
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

	byteValue, _ := ioutil.ReadAll(jsonFile)

	var result map[string]interface{}
	err = json.Unmarshal([]byte(byteValue), &result)

	return result, err
}

func zipOutputToBase64(output_path string) (string, error) {
	output_path, err := filepath.Abs(output_path)
	if err != nil {
		log.Printf("<3>Cannot resolve absolute form of output_path (%s) %v\n", output_path, err)
		return "", err
	}

	f, err := ioutil.TempFile("", "output*")
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

	data, err := ioutil.ReadFile(f.Name())
	if err != nil {
		log.Println("<3>Reading of file failed", err)
		return "", err
	}

	return base64.StdEncoding.EncodeToString(data), nil
}

func processMessages(ctx context.Context, wg *sync.WaitGroup) {

	defer wg.Done() // let main know we are done cleaning up

	args := GetArguments()

	for {

		select {

		case <-ctx.Done(): // if cancel() execute
			log.Println("<6>Gracefully canceling ProcessMessages loop...")
			return

		default:

			log.Println("<6>Get message via http request")

			resp, err := http.Get(args.MqReadServiceAddr)
			if err != nil {
				log.Println(err)
				continue
			}

			msg := requestMessage{
				MaxRunTime: 500, // 300 for test and 200 for build
				Memory:     2048,
			}

			readOk := func() bool {
				defer resp.Body.Close()

				log.Println("<6>Status code returned from HTTP GET ", resp.StatusCode)

				if resp.StatusCode == 404 {
					log.Println("<6>Empty response. No messages in input queue.")
					return false
				}

				if resp.StatusCode < 200 || resp.StatusCode >= 300 {
					log.Println("<4>Error mqreadservice. No messages returned.")
					return false
				}

				body, err := ioutil.ReadAll(resp.Body)
				if err != nil {
					log.Println(err)
					return false
				}

				// check payload against json scheme to validate it
				jsonDocument := gojsonschema.NewBytesLoader(body)

				result, err := schema.Validate(jsonDocument)
				if err != nil {
					log.Println("<4>Cannot validate json against schema", err)
					return false
				}

				if !result.Valid() {
					log.Println("<4>Json schema validation failed", result.Errors())
					return false
				}

				if err := json.Unmarshal(body, &msg); err != nil {
					log.Println("<4>Cannot parse json", err)
					return false
				}

				return true
			}()

			// if there was a problem with getting a TestRun case, then we cannot process it
			// and we go for next iteration of loop trying to get another TestRun case
			if !readOk {
				continue
			}

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

				log.Println("<6>Start processing of message.")

				var outputVolume docker.DockerVolume
				// we do not want to delte the tmp files, it may be useful,
				// also the line below will not do the trick, since args
				// are bound when defer is called, not when the function is
				// called, so it will call Cleanup on empty path :(
				//defer outputVolume.Cleanup()

				result := func() string {

					ctx := context.Background()

					config := docker.DockerConfig{
						Volumes:     []docker.DockerVolume{},
						DockerImage: msg.DockerImage,
						Timeout:     uint16(msg.MaxRunTime),
						Memory:      int64(msg.Memory * 1024 * 1024),
						Username:    args.DockerUsername,
						Password:    args.DockerPassword,
					}

					docker.PullImage(ctx, config)

					env, err := docker.GetDockerEnv(ctx, msg.DockerImage)
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
							log.Println("<3>Cannot write submission file", err)
							return err.Error()
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
						return err.Error()
					}

					return result
				}()

				// this is path for output from our container (very not standard, but whatever)
				outputPath := outputVolume.HostPath

				// save whole message there so it will be available in the zip file
				msgJson, err := json.MarshalIndent(msg, "", " ")
				if err != nil {
					log.Println("<4>Cannot save msg to json", err)
					msgJson = []byte(err.Error())
				}

				tmp, err := ioutil.TempFile(outputPath, "__msg__*.json")
				if err == nil {
					_, err = tmp.Write(msgJson)
					tmp.Close()
					defer os.Remove(tmp.Name())
				}

				if err != nil {
					log.Println("<4>Cannot write json", err)
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
}

func Run(ctx context.Context, out io.Writer) int {

	pmCtx, pmCancel := context.WithCancel(ctx)

	log.SetOutput(out)
	log.SetFlags(0)

	signalChan := make(chan os.Signal, 1)
	signal.Notify(signalChan, os.Interrupt, unix.SIGTERM)
	defer signal.Stop(signalChan)

	log.Println("<6>Queued is starting.")

	defer func() {
		r := recover()
		if r != nil {
			log.Panicln("<3>Panicing ", r)
		}
	}()

	schema = getSchema()

	exitDone := &sync.WaitGroup{}
	exitDone.Add(1)

	// start process messages queue
	go func() {
		processMessages(pmCtx, exitDone)
	}()

	<-signalChan // wait for signal
	log.Printf("<6>Got SIGINT/SIGTERM, exiting...\n")
	pmCancel()

	// wait for goroutine to stop
	exitDone.Wait()

	log.Println("<6>Queued has ended.")

	return 0
}
