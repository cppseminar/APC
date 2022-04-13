package main

import (
	"fmt"
	"log"
	"os"

	"go.temporal.io/sdk/client"
	"go.temporal.io/sdk/worker"

	app "workers/test-all-students"
)

func main() {
	fmt.Println("Hello, world.")
	fmt.Println(os.Getenv("TEMPORAL_SERVER"))

	c, err := client.NewClient(client.Options{
		HostPort: os.Getenv("TEMPORAL_SERVER"),
	})
	if err != nil {
		log.Fatalln("Unable to create Temporal client", err)
	}
	defer c.Close()

	w := worker.New(c, app.TestAllStudentsTaskQueue, worker.Options{})
	w.RegisterWorkflow(app.TestAllStudentsWorkflow)
	w.RegisterWorkflow(app.RunNewestSubmissionForUser)

	w.RegisterActivity(app.GetAllUsers)
	w.RegisterActivity(app.GetNewestSubmissionIdForTask)
	w.RegisterActivity(app.GetTaskId)
	w.RegisterActivity(app.RunTest)
	w.RegisterActivity(app.GetSubmissionContentUrl)
	// Start listening to the Task Queue
	err = w.Run(worker.InterruptCh())
	if err != nil {
		log.Fatalln("Unable to start Worker", err)
	}
}
