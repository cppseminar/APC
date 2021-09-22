package queue

import (
	"flag"
	"log"
	"os"
	"sync"
)

type Arguments struct {
	ServerHost string
	ServerPort int
}

func parseArgs() Arguments {
	serverHost := flag.String("host", "", "server host of queue service")
	serverPort := flag.Int("port", 0, "server port where queue is running (mandatory)")

	flag.CommandLine.SetOutput(log.Writer())
	flag.Parse()

	if *serverPort == 0 {
		log.Println("Wrong parameters given")
		flag.Usage()
		os.Exit(1)
	}

	return Arguments{
		ServerHost: *serverHost,
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
