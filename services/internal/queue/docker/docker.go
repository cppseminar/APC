package docker

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"strconv"
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
	Volumes []DockerVolume
	// Name of docker image, that will be run
	DockerImage string
	// Timeout in seconds, container will be killed after expiring
	Timeout uint16
	// Memory Max ram that container can use. Number of bytes or 0 for infinite
	Memory int64
	// Docker credentials
	Username string
	Password string
}

// DockerVolume This type should have DockerVolume.Cleanup() called on deletion
type DockerVolume struct {
	// Path of directory in this filesystem
	HostPath string
	// Volume under which is this path known to container
	GuestPath string
	// whether it is read only
	ReadOnly bool
}

// Cleanup should be called on DockerVolume deletion
func (volume DockerVolume) Cleanup() {
	err := os.RemoveAll(volume.HostPath)
	if err != nil {
		log.Printf("[WARNING] Error deleting tmp folder %v with error %v\n", volume.HostPath, err)
	}
}

func (volume DockerVolume) GetMount() string {
	if volume.ReadOnly {
		return fmt.Sprintf("%s:%s", volume.HostPath, volume.GuestPath)
	} else {
		return fmt.Sprintf("%s:%s:rw", volume.HostPath, volume.GuestPath)
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
			if strings.Contains(err.Error(), "is not running") {
				// This is failsafe, there is small probability in timeouts going
				// so funny, that after context expiry, this container would
				// actually stop. In that case we don't want to panic
				log.Printf("WARNING: Please research this case further")
				return
			} else if strings.Contains(err.Error(), "No such container") {
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
	defer killContainerOnBadCtx(ctx, dockerCli, containerID)
	var containerWaitC <-chan bool = waitExit(ctx, dockerCli, containerID)

	response, err := dockerCli.ContainerAttach(ctx, containerID,
		types.ContainerAttachOptions{
			Stream: true,
			Stdout: true,
			Stderr: true,
		})

	if err != nil {
		return "", "", fmt.Errorf("error on docker attach: %v", err.Error())
	}

	err = dockerCli.ContainerStart(ctx, containerID, types.ContainerStartOptions{})
	if err != nil {
		return "", "", fmt.Errorf("error on docker containerstart: %v", err.Error())
	}

	var returnSuccess bool = <-containerWaitC

	if !returnSuccess {
		// Container run returned nonzero return code. This is potentially
		// dangerous, so let's log everything and return error
		return "", "", errors.New("container exited incorrectly")
	}

	stdout, stderr := strings.Builder{}, strings.Builder{}
	_, err = stdcopy.StdCopy(&stdout, &stderr, response.Reader)
	if err != nil {
		return "", "", err
	}

	return stdout.String(), stderr.String(), nil
}

func PullImage(ctx context.Context, config DockerConfig) {
	ctx, cancel := context.WithTimeout(ctx, time.Duration(10)*time.Minute)
	defer cancel()

	authConfig := types.AuthConfig{
		Username: config.Username,
		Password: config.Password,
	}
	encodedJSON, err := json.Marshal(authConfig)
	if err != nil {
		log.Println("Error while marshal json, error:", err)
		return
	}

	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		log.Printf("Error while creating docker client: %v\n", err)
		return
	}

	reader, err := cli.ImagePull(ctx, config.DockerImage, types.ImagePullOptions{
		RegistryAuth: base64.URLEncoding.EncodeToString(encodedJSON),
	})
	if err != nil {
		log.Printf("Error while pulling docker image (%v): %v\n", config.DockerImage, err)
		return
	}

	defer reader.Close()
	_, err = io.Copy(ioutil.Discard, reader)
	if err != nil {
		log.Printf("Unable to pull image: %v\n", err)
		return
	}
}

func GetDockerEnv(ctx context.Context, containerId string) (map[string]string, error) {
	context, cancel := context.WithTimeout(ctx, time.Duration(int64(30))*time.Second)
	defer cancel()

	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		log.Printf("Error while creating docker client: %v\n", err)
		return nil, err
	}

	var dockerContainerConfig = &container.Config{
		Image:           containerId,
		NetworkDisabled: true,
	}
	var dockerHostConfig = &container.HostConfig{
		AutoRemove:  true,
		NetworkMode: "none",
	}

	container, err := cli.ContainerCreate(context, dockerContainerConfig, dockerHostConfig, nil, nil, "")
	if err != nil {
		log.Printf("Error while creating docker image (%v): %v\n", containerId, err)
		return nil, err
	}

	json, err := cli.ContainerInspect(context, container.ID)
	if err != nil {
		log.Printf("Error while inspecting docker container %v: %v\n", containerId, err)
		return nil, err
	}

	result := map[string]string{}
	for _, x := range json.Config.Env {
		p := strings.SplitN(x, "=", 2)
		result[p[0]] = p[1]
	}

	return result, nil
}

// DockerExec Execute docker image, identified by config.
// This is blocking call. In the end, stdout will be returned by output string
func DockerExec(ctx context.Context, config DockerConfig) (string, error) {
	// Let's always add 2 seconds to timeout, for startup and so on
	ctx, cancel := context.WithTimeout(ctx, time.Duration(int64(config.Timeout)+2)*time.Second)
	defer cancel()

	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		log.Printf("Error while creating docker client: %v\n", err)
		return "", err
	}

	var dockerConfig = &container.Config{
		Image:           config.DockerImage,
		NetworkDisabled: true,
	}

	var dockerHostConfig = &container.HostConfig{
		AutoRemove:  true,
		NetworkMode: "none",
		Resources: container.Resources{
			Memory: config.Memory,
		},
	}

	if config.Volumes != nil {
		dockerHostConfig.Binds = []string{}
		for _, volume := range config.Volumes {
			dockerHostConfig.Binds = append(dockerHostConfig.Binds, volume.GetMount())
		}
	}

	container, err := cli.ContainerCreate(ctx, dockerConfig, dockerHostConfig, nil, nil, "")
	if err != nil {
		log.Printf("Error while creating docker container (%v): %v\n", config.DockerImage, err)
		return "", err
	}

	_, stderr, err := runDocker(ctx, cli, container.ID)

	select {
	case <-ctx.Done():
		// Timeout expired. Something must have gone very wrong.
		// Let's prepend to error some text
		err = errors.New("TIMEOUT expired! " + ctx.Err().Error())
	default:
		// Happy path
		// Fall through here
	}

	if err != nil {
		log.Printf("Error: %v\tConfig: %#v\n", err.Error(), config)
		return "", err
	}

	return stderr, nil
}
