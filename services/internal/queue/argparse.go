package queue

import (
	"encoding/json"
	"flag"
	"io/ioutil"
	"log"
	"os"
	"sync"
)

type Arguments struct {
	ServerHost     string
	ServerPort     int
	DockerUsername string
	DockerPassword string
}

func parseArgs() Arguments {
	serverHost := flag.String("host", "0.0.0.0", "server host of queue service")
	serverPort := flag.Int("port", 0, "server port where queue is running (mandatory)")
	configFile := flag.String("config", "", "configuration file")

	flag.CommandLine.SetOutput(log.Writer())
	flag.Parse()

	if *serverPort == 0 {
		log.Println("Wrong parameters given")
		flag.Usage()
		os.Exit(1)
	}

	var result Arguments

	if *configFile != "" {
		content, err := ioutil.ReadFile(*configFile)
		if err != nil {
			log.Println("Cannot read file, error:", err)
			os.Exit(1)
		}
		if err := json.Unmarshal(content, &result); err != nil {
			log.Println("Cannot parse json, error:", err)
			os.Exit(1)
		}
	}

	if *serverHost != "" {
		result.ServerHost = *serverHost
	}

	if *serverPort != 0 {
		result.ServerPort = *serverPort
	}

	return result
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
