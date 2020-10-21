package docker

import (
	"context"
	"errors"
	"log"
	"os"
	"path/filepath"
	"strings"

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
	// Timeout in seconds, container will be killed after expiring
	Timeout int64
	// Max ram, either nil, or pointer to string specifying memory in bytes
	Memory *int64
}

// DockerVolume This type should have DockerVolume.Cleanup() called on deletion
type DockerVolume struct {
	// Path of directory in this filesystem
	DirPath string
	// Volume under which is this path known, or empty
	Volume string
	// Whether Cleanup should wipe dirPath folder
	RmDir bool
}

// Cleanup should be called on DockerVolume deletion
func (volume DockerVolume) Cleanup() {
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
	if volume.RmDir {
		err = os.Remove(volume.DirPath)
		if err != nil {
			log.Printf("Error deleting tmp folder %v %v", volume.DirPath, err)
		}
	}

}

func waitExit(ctx context.Context, dockerCli *client.Client, containerID string) <-chan bool {
	if len(containerID) == 0 {
		// containerID can never be empty
		panic("Error: waitExit needs a containerID as parameter")
	}

	// WaitConditionNextExit is used to wait for the next time the state changes
	// to a non-running state. If the state is currently "created" or "exited",
	// this would cause Wait() to block until either the container runs and exits
	// or is removed.
	resultC, errC := dockerCli.ContainerWait(ctx, containerID, container.WaitConditionNextExit)

	statusC := make(chan bool, 1)
	go func() {
		select {
		case result := <-resultC:
			if result.Error != nil || result.StatusCode != 0 {
				log.Printf("Container returned error return code %#v\n", result)
				statusC <- false
				return
			}
			statusC <- true

		case <-errC:
			log.Println("Error in attach to container")
			statusC <- false
		}
	}()

	return statusC
}

func formatVolume(volume DockerVolume) string {
	// This /sources value is where I usually put source code in tester scripts.
	// There is nothing preventing you from changing this convention, or
	// parametrizing this....
	if volume.Volume != "" {
		return volume.Volume + `:/sources`
	}
	return volume.DirPath + `:/sources`
}

// DockerExec Execute docker image, identified by config.
// This is blocking call. In the end, stdout will be returned by output string
func DockerExec(config DockerConfig) (string, error) {
	var errorMessage = errors.New("Error occured and tests were not executed!")
	var memory int64 = 0 // Infinite memory by default

	if config.Memory != nil {
		memory = *config.Memory
	}

	formattedVolume := formatVolume(config.Volume)

	// TODO: Context should be cancellable, for docker timeout
	ctx := context.Background()
	cli, err := client.NewEnvClient()

	if err != nil {
		log.Printf("Error while creating docker client: %v", err)
		return "", errorMessage
	}

	var dockerContainerConfig = &container.Config{Image: config.DockerImage}
	var dockerHostConfig = &container.HostConfig{
		Binds: []string{formattedVolume},
		Resources: container.Resources{
			Memory: memory,
		},
	}

	container, err := cli.ContainerCreate(ctx, dockerContainerConfig, dockerHostConfig, nil, "")
	if err != nil {
		log.Printf("Error while creating docker image (%v): %v",
			config.DockerImage, err)
		return "", errorMessage
	}

	// This should delete all not running containers
	defer cli.ContainersPrune(ctx, filters.Args{})

	var containerWaitC <-chan bool = waitExit(ctx, cli, container.ID)

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
	var returnSuccess bool = <-containerWaitC

	if !returnSuccess {
		// Container run returned nonzero return code. This is potentially
		// dangerous, so let's log everything and return error
		log.Printf("Container exited incorrectly. Config: %#v\n", config)
		return "", errorMessage
	}

	stdout, stderr := strings.Builder{}, strings.Builder{}
	stdcopy.StdCopy(&stdout, &stderr, response.Reader)
	if stderr.String() != "" {
		log.Println("Docker container has output on stderr")
		log.Println(stderr.String())
	}
	return stdout.String(), nil
}
