package queue

import (
	"flag"
	"log"
	"os"
	"sync"
)

type Arguments struct {
	ServerURL  string
	ServerPort int
}

func parseArgs() Arguments {
	serverUrl := flag.String("url", "", "server url of queue service")
	serverPort := flag.Int("port", 0, "server port where queue is running mandatory")

	flag.CommandLine.SetOutput(log.Writer())
	flag.Parse()

	if *serverPort == 0 {
		log.Println("Wrong parameters given")
		flag.Usage()
		os.Exit(1)
	}

	return Arguments{
		ServerURL:  *serverUrl,
		ServerPort: *serverPort,
	}
}

var (
	argumentsOnce sync.Once
	arguments     Arguments
)

func GetArguments() Arguments {
	argumentsOnce.Do(func() {
		arguments = parseArgs()
	})

	return arguments
}
