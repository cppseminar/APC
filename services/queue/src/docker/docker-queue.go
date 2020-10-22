package docker

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/client"
	"github.com/docker/docker/pkg/stdcopy"
)

// DockerConfig configuration for one run of docker image. Used by DockerExec
type DockerConfig struct {
	// File path to folder mounted as /source (should contain source files)
	Volume DockerVolume
	// Name of docker image, that will be run
	DockerImage string
	// Timeout in seconds, container will be killed after expiring
	Timeout uint16
	// Memory Max ram that container can use. Either nil which means no limits,
	// or number of bytes
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
				log.Printf("Container returned error code\n\t%#v\n", result)
				statusC <- false
				return
			}
			statusC <- true

		case err := <-errC:
			log.Printf("Error in container wait: %v\n", err)
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

// If ctx is expired, try to kill container
// Do not reuse this function, it serves very specific use case
func killContainerOnBadCtx(ctx context.Context, dockerCli *client.Client, containerID string) {
	select {
	case <-ctx.Done():
		// This is already bad state, let's try to kill container and hope for
		// the best
		newCtx, cancel := context.WithTimeout(context.Background(), time.Second*3)
		defer cancel()
		err := dockerCli.ContainerKill(newCtx, containerID, "KILL")
		if err != nil {
			if strings.Index(err.Error(), "is not running") != -1 {
				// This is failsafe, there is small probability in timeouts going
				// so funny, that after context expiry, this container would
				// actually stop. In that case we don't want to panic
				log.Printf("WARNING: Please research this case further")
				return
			} else if strings.Index(err.Error(), "No such container") != -1 {
				// Same as above
				log.Printf("WARNING: Please research this case further")
				return
			}

			panic("Container kill after timeout failed!" + err.Error())
		}
		log.Printf("Container kill successful %v", containerID)
	default:
		// Context is not expired. This was just deffered call, but container is
		// already dead. This happens all the time and is expected.
	}
}

// Run container identified by containerID. Returns stdout, stderr, error
// This function doesn't log anything, insteads returns detailed error messages
func runDocker(ctx context.Context, dockerCli *client.Client, containerID string) (string, string, error) {
	newCancelableContext, cancel := context.WithCancel(ctx)
	defer cancel()

	defer killContainerOnBadCtx(newCancelableContext, dockerCli, containerID)
	var containerWaitC <-chan bool = waitExit(newCancelableContext, dockerCli, containerID)

	response, err := dockerCli.ContainerAttach(newCancelableContext, containerID,
		types.ContainerAttachOptions{
			Stdout: true,
			Stream: true,
			Stderr: true,
		})

	if err != nil {
		cancel()
		eMessage := fmt.Sprintf("Error on docker attach: %v", err.Error())
		return "", "", errors.New(eMessage)
	}

	err = dockerCli.ContainerStart(newCancelableContext, containerID, types.ContainerStartOptions{})
	if err != nil {
		cancel()
		eMessage := fmt.Sprintf("Error on docker containerstart: %v", err.Error())
		return "", "", errors.New(eMessage)
	}

	var returnSuccess bool = <-containerWaitC

	if !returnSuccess {
		// Container run returned nonzero return code. This is potentially
		// dangerous, so let's log everything and return error
		return "", "", errors.New("Container exited incorrectly")
	}

	stdout, stderr := strings.Builder{}, strings.Builder{}
	stdcopy.StdCopy(&stdout, &stderr, response.Reader)
	return stdout.String(), stderr.String(), nil
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

	// Let's always add 2 seconds to timeout, for startup and so on
	context, cancelContext := context.WithTimeout(
		context.Background(),
		time.Duration(int64(config.Timeout)+2)*time.Second,
	)
	defer cancelContext()

	cli, err := client.NewEnvClient()

	if err != nil {
		log.Printf("Error while creating docker client: %v\n", err)
		return "", errorMessage
	}

	var dockerContainerConfig = &container.Config{
		Image:           config.DockerImage,
		NetworkDisabled: true,
	}
	var dockerHostConfig = &container.HostConfig{
		Binds:       []string{formattedVolume},
		AutoRemove:  true,
		NetworkMode: "none",
		Resources: container.Resources{
			Memory: memory,
		},
	}

	container, err := cli.ContainerCreate(context, dockerContainerConfig, dockerHostConfig, nil, "")
	if err != nil {
		log.Printf("Error while creating docker image (%v): %v\n",
			config.DockerImage, err)
		return "", errorMessage
	}

	stdout, _, err := runDocker(context, cli, container.ID)

	select {
	case <-context.Done():
		// Timeout expired. Something must have gone very wrong.
		// Let's prepend to error some text
		if err == nil {
			err = errors.New("")
		}

		err = errors.New("TIMEOUT expired!\n" + err.Error())
	default:
		// Happy path
		// Fall through here
	}

	if err != nil {
		log.Printf("Error: %v\n\tConfig: %#v\n", err.Error(), config)
		return "", errorMessage
	}

	return stdout, nil
}
