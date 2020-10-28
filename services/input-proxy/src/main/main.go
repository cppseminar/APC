package main

import (
	"bytes"
	"encoding/base64"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"

	"services/input-proxy/cmd"

	"gopkg.in/square/go-jose.v2"
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

func buildForwardURL(secure bool, host string, originalUrl url.URL) (string) {
	var scheme string  = "https"
	if !secure {
		scheme = "http"
	}
	originalUrl.Scheme = scheme
	originalUrl.Host = host
	originalUrl.User = nil
	return originalUrl.String()
}

func verifyJWSAndExtractPayload(body []byte) ([]byte, error) {
	object, err := jose.ParseSigned(string(body))
	if err != nil {
		log.Println("Cannot parse body as JWS '", string(body), "'.")
		return nil, err
	}

	privateKey, err := getSigningKey()
	if err != nil {
		panic(fmt.Sprintf("Bad env value for signing key %v", err))
	}
	var key jose.JSONWebKey
	key.UnmarshalJSON([]byte(fmt.Sprintf(`{
    "kty": "oct",
    "use": "sig",
    "k": "%v",
    "alg": "HS256"
	}`, privateKey)))

	// i'm kind of scared from jose, so I added here these paranoid checks
	// https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/?_ga=2.1739384.896580470.1599590522-1256792510.1597065586
	if len(object.Signatures) != 1 {
		return nil, errors.New("only one signature is allowed")
	}

	if object.Signatures[0].Header.Algorithm != "HS256" {
		return nil, errors.New("only HS256 is allowed as signing algorithm")
	}

	output, err := object.Verify(&key)
	if err != nil {
		return nil, err
	}

	return output, nil
}

func processRequest(r *http.Request, destination string) int {
	if r.Method != "POST" {
		log.Println("Only post requests are supported!")
		return http.StatusBadRequest
	}

	req, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Println(err)
		return http.StatusInternalServerError
	}

	payload, err := verifyJWSAndExtractPayload(req)
	if err != nil {
		log.Println(err)
		return http.StatusUnauthorized
	}

	// so here the request is verified, we are good to go
	resp, err := client.Post(destination, "text/json", bytes.NewReader(payload))
	if err != nil {
		log.Println(err)
		return http.StatusInternalServerError
	}

	// forward the error code
	return resp.StatusCode
}

var tr = &http.Transport{
	ResponseHeaderTimeout:  10 * time.Second,
	IdleConnTimeout:        30 * time.Second,
	MaxResponseHeaderBytes: 1024,
}

var client = &http.Client{Transport: tr}

// key should be base64 encoded


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
		Host: parsedURL.Host,
	}).String(), nil
}

func createHandler(forwardURL string) (func(http.ResponseWriter, *http.Request), error) {
	var parsedURL string
	var err error

	if parsedURL, err = parseParamURL(forwardURL); err != nil {
		return nil, err
	}

	log.Printf("Proxy will forward requests to %v", parsedURL)


	handler := func (w http.ResponseWriter, r *http.Request) {
		// limit body size to something sensible https://stackoverflow.com/q/28282370/4807781
		r.Body = http.MaxBytesReader(w, r.Body, 100000)
		err := r.ParseForm()
		if err != nil {
			log.Println(err)
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		status := processRequest(r, parsedURL)
		if status != http.StatusOK {
			log.Println("Request",
				r.Method,
				r.Host,
				r.Proto,
				"remote addr", r.RemoteAddr,
				"ended up with status", status)
		}

		w.WriteHeader(status)
	}


	return handler, nil
}

