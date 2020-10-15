package docker

import (
	"log"
	"errors"
	"context"
	"strings"
	"os"
	"path/filepath"


	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/filters"
	"github.com/docker/docker/client"
	"github.com/docker/docker/pkg/stdcopy"
)

// DockerConfig DockerExec configuration
type DockerConfig struct {
	// File path to folder mounted as /source (should contain source files)
	Volume DockerVolume
	// Name of docker image, that will be run
	DockerImage string
}

// DockerVolume This type should have DockerVolume.Cleanup() called on deletion
type DockerVolume struct {
	// Path of directory in this filesystem
	DirPath string
	// Volume under which is this path known, or empty
	Volume  string
	// Whether Cleanup should wipe dirPath folder
	RmDir   bool
}

// Cleanup should be called on DockerVolume deletion
func (volume DockerVolume) Cleanup() {
	if volume.RmDir {
		panic("Not implemented tmp folder deletion")
	}

	d, err := os.Open(volume.DirPath)
	if err != nil {
		return
	}
	defer d.Close()
	names, err := d.Readdirnames(-1)
	if err != nil {
		return
	}
	for _, name := range names {
		err = os.RemoveAll(filepath.Join(volume.DirPath, name))
	}
}

func waitExit(ctx context.Context, dockerCli *client.Client, containerID string) <-chan int {
	if len(containerID) == 0 {
		// containerID can never be empty
		panic("Internal Error: waitExit needs a containerID as parameter")
	}

	// WaitConditionNextExit is used to wait for the next time the state changes
	// to a non-running state. If the state is currently "created" or "exited",
	// this would cause Wait() to block until either the container runs and exits
	// or is removed.
	resultC, errC := dockerCli.ContainerWait(ctx, containerID, container.WaitConditionNextExit)

	statusC := make(chan int)
	go func() {
		select {
		case result := <-resultC:
			if result.Error != nil {
				statusC <- 125
			} else {
				statusC <- int(result.StatusCode)
			}
		case <-errC:
			log.Println("Error in attach to container")
			statusC <- 125
		}
	}()

	return statusC
}

func formatVolume(volume DockerVolume) string {
	if volume.Volume != "" {
		return volume.Volume + `:/sources`
	}
	return volume.DirPath + `:/sources`
}

// DockerExec Execute docker image, identified by config.
// This is blocking call. In the end, stdout will be returned by output string
func DockerExec(config DockerConfig) (string, error) {
	var errorMessage = errors.New("Error occured tests were not executed")

	formattedVolume := formatVolume(config.Volume)

	// TODO: Context should be cancellable, for docker timeout
	ctx := context.Background()
	cli, err := client.NewEnvClient()

	if err != nil {
		log.Printf("Error while creating docker client: %v", err)
		return "", errorMessage
	}

	var dockerContainerConfig = &container.Config{Image: config.DockerImage}
	var dockerHostConfig = &container.HostConfig{Binds: []string{formattedVolume}}

	container, err := cli.ContainerCreate(ctx, dockerContainerConfig, dockerHostConfig, nil, "")
	if err != nil {
		log.Printf("Error while creating docker image (%v): %v",
			config.DockerImage, err)
		return "", errorMessage
	}
	var containerWaitC = waitExit(ctx, cli, container.ID)

	// This should delete all not running containers
	defer cli.ContainersPrune(ctx, filters.Args{})

	response, err := cli.ContainerAttach(ctx, container.ID,
		types.ContainerAttachOptions{
			Stdout: true,
			Stream: true,
			Stderr: true,
		})

	if err != nil {
		log.Printf("Error on docker attach: %v", err)
		return "", errorMessage
	}

	err = cli.ContainerStart(ctx, container.ID, types.ContainerStartOptions{})

	if err != nil {
		log.Printf("Error on docker image (%v) start: %v", config.DockerImage, err)
		return "", errorMessage
	}
	// Wait for container to finish
	<-containerWaitC
	stdout, stderr := strings.Builder{}, strings.Builder{}
	stdcopy.StdCopy(&stdout, &stderr, response.Reader)
	return stdout.String(), nil
}

