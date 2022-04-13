package app

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"path"
)

type Submission struct {
	Id      string
	Content string
}

func GetAllUsers() ([]string, error) {
	service, err := url.Parse(os.Getenv("USER_SERVICE"))
	if err != nil {
		log.Println("Unable to parse USER_SERVICE env", err)
		return nil, err
	}
	service.Path = path.Join(service.Path, "user")

	resp, err := http.Get(service.String())
	if err != nil {
		log.Println("Unable to get users list", err)
		return nil, err
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("Unable to get body from http response", err)
		return nil, err
	}

	var users []string
	if err := json.Unmarshal(body, &users); err != nil {
		log.Println("Unable to parse json", err)
		return nil, err
	}

	return users, nil
}

func GetNewestSubmissionIdForTask(user string, taskId string) (string, error) {
	service, err := url.Parse(os.Getenv("SUBMISSIONS_SERVICE"))
	if err != nil {
		log.Println("Unable to parse SUBMISSIONS_SERVICE env", err)
		return "", err
	}
	service.Path = path.Join(service.Path, fmt.Sprintf("submission/%s?taskId=%s", user, taskId))

	resp, err := http.Get(service.String())
	if err != nil {
		log.Println("Unable to get submissions list", err)
		return "", err
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("Unable to get body from http response", err)
		return "", err
	}

	var submissions []Submission
	if err := json.Unmarshal(body, &submissions); err != nil {
		log.Println("Unable to parse json", err)
		return "", err
	}

	if len(submissions) == 0 {
		return "", nil
	}

	return submissions[0].Id, nil
}

func GetSubmissionContentUrl(user string, submissionId string) (string, error) {
	service, err := url.Parse(os.Getenv("SUBMISSIONS_SERVICE"))
	if err != nil {
		log.Println("Unable to parse SUBMISSIONS_SERVICE env", err)
		return "", err
	}
	service.Path = path.Join(service.Path, fmt.Sprintf("submission/%s/%s?contentFormat=url", user, submissionId))

	resp, err := http.Get(service.String())
	if err != nil {
		log.Println("Unable to get submission", err)
		return "", err
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("Unable to get body from http response", err)
		return "", err
	}

	var submission Submission
	if err := json.Unmarshal(body, &submission); err != nil {
		log.Println("Unable to parse json", err)
		return "", err
	}

	return submission.Content, nil
}

func GetTaskId(testCaseId string) (string, error) {
	service, err := url.Parse(os.Getenv("TEST_SERVICE"))
	if err != nil {
		log.Println("Unable to parse TEST_SERVICE env", err)
		return "", err
	}
	service.Path = path.Join(service.Path, fmt.Sprintf("cases/%s", testCaseId))

	resp, err := http.Get(service.String())
	if err != nil {
		log.Println("Unable to get test case", err)
		return "", err
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("Unable to get body from http response", err)
		return "", err
	}

	type TestCase struct {
		Id     string
		TaskId string
	}

	var testCase TestCase
	if err := json.Unmarshal(body, &testCase); err != nil {
		log.Println("Unable to parse json", err)
		return "", err
	}

	return testCase.TaskId, nil
}

func RunTest(request TestRequest) error {
	service, err := url.Parse(os.Getenv("TEST_SERVICE"))
	if err != nil {
		log.Println("Unable to parse TEST_SERVICE env", err)
		return err
	}
	service.Path = path.Join(service.Path, "test")

	json_data, err := json.Marshal(request)

	if err != nil {
		log.Println("Unable to marshal json", err)
		return err
	}

	resp, err := http.Post(service.String(), "application/json", bytes.NewBuffer(json_data))
	if err != nil {
		log.Println("Unable to post test", err)
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Println("Non-OK HTTP status:", resp.StatusCode)
		// You may read / inspect response body
		return fmt.Errorf("HTTP request failed with status %d", resp.StatusCode)
	}

	_, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("Unable to get body from http response", err)
		return err
	}

	return nil
}
