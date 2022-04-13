package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"
	app "workers/test-all-students"

	"github.com/gorilla/mux"
	"go.temporal.io/sdk/client"
)

var temporal client.Client

func runTests(w http.ResponseWriter, r *http.Request) {
	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Println("Error reading body:", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	type RunTestsRequest struct {
		User       string
		TestCaseId string
	}

	var runTestsRequest RunTestsRequest
	if err := json.Unmarshal(body, &runTestsRequest); err != nil {
		log.Println("Unable to parse json", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	options := client.StartWorkflowOptions{
		TaskQueue:                app.TestAllStudentsTaskQueue,
		WorkflowExecutionTimeout: 15 * time.Minute,
	}

	request := app.TestRequest{
		CreatedBy:  runTestsRequest.User,
		TestCaseId: runTestsRequest.TestCaseId,
		Counted:    false,
	}

	we, err := temporal.ExecuteWorkflow(context.Background(), options, app.TestAllStudentsWorkflow, request)
	if err != nil {
		log.Println("Error starting Greeting workflow", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	response, err := json.Marshal(we.GetID())
	if err != nil {
		log.Println("Failed to format json", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	w.Write(response)
}

func getTests(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	testId, ok := vars["testId"]
	if !ok {
		fmt.Println("id is missing in parameters")
	}

	description, err := temporal.DescribeWorkflowExecution(context.Background(), testId, "")
	if err != nil {
		log.Println("Failed to get workflow", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	body, err := json.Marshal(description.WorkflowExecutionInfo.Status.String())
	if err != nil {
		log.Println("Failed to format json", err)
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	w.Write(body)
}

func catchAllHandler(w http.ResponseWriter, r *http.Request) {
	log.Printf("<3>Unsupported request %v %v ip %v\n", r.Method, r.URL.Path, r.RemoteAddr)
	w.WriteHeader(http.StatusNotFound)
}

func startHttpServer(serverURL string) {
	r := mux.NewRouter()
	r.HandleFunc("/tests", runTests).Methods("POST")
	r.HandleFunc("/tests/{testId}", getTests)
	r.NotFoundHandler = http.HandlerFunc(catchAllHandler)

	srv := &http.Server{
		Addr:         serverURL,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
		Handler:      r,
	}

	// always returns error. ErrServerClosed on graceful close
	if err := srv.ListenAndServe(); err != http.ErrServerClosed {
		log.Fatalf("<3>Listen and serve failed with: %v\n", err)
	} else {
		log.Println("<6>Server stopped gracefully...")
	}
}

func main() {
	var err error
	temporal, err = client.NewClient(client.Options{
		HostPort: os.Getenv("TEMPORAL_SERVER"),
	})
	if err != nil {
		log.Fatalln("Unable to create Temporal client", err)
	}
	defer temporal.Close()

	log.Println("<6>Starting http server ...")

	startHttpServer("0.0.0.0:80")
}
