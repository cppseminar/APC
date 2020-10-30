package main

import (
	"encoding/base64"
	"errors"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"bytes"
	"strings"
	"time"

	"services/input-proxy/cmd"
)

const envPrivateKey string = "APC_PRIVATE_KEY"

func getSigningKey() (string, error) {
	var privateKey string = strings.TrimSpace(os.Getenv(envPrivateKey))
	keyBytes, err := base64.StdEncoding.DecodeString(privateKey)
	if err != nil {
		return "", err
	}
	if len(keyBytes) == 0 {
		return "", errors.New("Empty signing key")
	}
	return strings.TrimRight(privateKey, "="), nil
}

func buildForwardURL(secure bool, host string, originalURL url.URL) string {
	var scheme string = "https"
	if !secure {
		scheme = "http"
	}
	originalURL.Scheme = scheme
	originalURL.Host = host
	originalURL.User = nil
	return originalURL.String()
}

var tr = &http.Transport{
	ResponseHeaderTimeout:  10 * time.Second,
	IdleConnTimeout:        30 * time.Second,
	MaxResponseHeaderBytes: 1024,
}

func main() {
	port, queueURL := cmd.Execute()
	log.Println("Input-proxy is starting")

	_, err := getSigningKey()
	if err != nil {
		log.Fatalf("Cannot retrieve private key from env %v", err)
	}

	serverHandler, err := createHandler(queueURL)
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("Proxy will listen on port %v", port)

	srv := &http.Server{
		Addr:         ":" + fmt.Sprint(port),
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
		Handler:      http.HandlerFunc(serverHandler),
	}

	err = srv.ListenAndServe()
	if err != nil {
		log.Fatal(err)
	}
}

// Given argument url, return either correct form url, or error
func parseParamURL(rawURL string) (string, error) {
	var parsedURL *url.URL
	var err error
	if parsedURL, err = url.Parse(rawURL); err != nil {
		return "", err
	}

	if parsedURL.Scheme != "http" && parsedURL.Scheme != "https" {
		return "", errors.New("Invalid/Unsupported scheme for proxy")
	}

	if parsedURL.Host == "" {
		return "", errors.New("URL has empty host")
	}
	return (&url.URL{
		Scheme: parsedURL.Scheme,
		Host:   parsedURL.Host,
	}).String(), nil
}

// Crates handler for http.Server. Handler will forward requests to forwardURL
func createHandler(forwardURL string) (func(http.ResponseWriter, *http.Request), error) {
	var parsedURL string
	var err error

	if parsedURL, err = parseParamURL(forwardURL); err != nil {
		return nil, err
	}

	log.Printf("Proxy will forward requests to %v", parsedURL)

	handler := func(w http.ResponseWriter, r *http.Request) {
		// limit body size to something sensible https://stackoverflow.com/q/28282370/4807781
		r.Body = http.MaxBytesReader(w, r.Body, 100000)
		err := r.ParseForm()
		if err != nil {
			log.Println(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		privateKey, err := getSigningKey()
		if err != nil {
			panic(fmt.Sprintf("Bad env value for signing key %v", err))
		}

		payload, err := verifyAndExtract(r, privateKey)
		if err != nil {
			log.Printf("Error %v \nWrong request:\n%#v", err, r)
			w.WriteHeader(400)
			return
		}

		client := http.Client{
			Timeout: 5 * time.Second,
		}

		// Here we really don't expect ANY errors, because this url was just
		// built few lines above.
		forwardURL, _ := url.Parse(parsedURL)


		queueURL := buildForwardURL(forwardURL.Scheme == "https",forwardURL.Host, *r.URL)
		internalRequest, err := http.NewRequest(r.Method, queueURL, bytes.NewReader(payload))
		if  err != nil {
			log.Printf("Cannot create forward request %v", err)
			w.WriteHeader(500)
			return
		}

		internalResponse, err := client.Do(internalRequest)
		if err != nil {
			log.Printf("Forward request error %v", err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		}


		defer internalResponse.Body.Close()

		responseBody := bytes.Buffer{}

		if _ ,err = responseBody.ReadFrom(internalResponse.Body); err != nil {
			log.Println("Error reading response from queue")
			log.Println(*internalRequest)
			log.Println(err)
			w.WriteHeader(http.StatusInternalServerError)
			return
		} else {
			w.WriteHeader(internalResponse.StatusCode)
			w.Write(responseBody.Bytes())
		}
	}
	return handler, nil
}
