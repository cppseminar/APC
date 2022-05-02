package main

import (
	"context"
	"os"
	"services/internal/queue"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())

	defer cancel()

	// let's log on stdout, so we are a well behaved daemon :)
	os.Exit(queue.Run(ctx, os.Stdout))
}
