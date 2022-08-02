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
	DockerUsername string
	DockerPassword string
}

func parseArgs() Arguments {
	configFile := flag.String("config", "", "configuration file")

	flag.CommandLine.SetOutput(log.Writer())
	flag.Parse()

	var result Arguments

	if *configFile != "" {
		content, err := ioutil.ReadFile(*configFile)
		if err != nil {
			log.Println("<3>Cannot read file, error:", err)
			os.Exit(1)
		}
		if err := json.Unmarshal(content, &result); err != nil {
			log.Println("<3>Cannot parse json, error:", err)
			os.Exit(1)
		}
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
