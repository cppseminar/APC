package main

import (
	"bytes"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"gopkg.in/natefinch/lumberjack.v2"
	"gopkg.in/square/go-jose.v2"
)

func verifyJWSAndExtractPayload(body []byte) ([]byte, error) {
	object, err := jose.ParseSigned(string(body))
	if err != nil {
		log.Println("Cannot parse body as JWS '", string(body), "'.", err)
		return nil, err
	}

	// this we should load from environment
	var key jose.JSONWebKey
	key.UnmarshalJSON([]byte(fmt.Sprintf(`{
    "kty": "oct",
    "use": "sig",
    "k": "%v",
    "alg": "HS256"
	}`, privateKey)))

	// i'm kind of scared from jose, so I add here those paranoid checks
	// https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/?_ga=2.1739384.896580470.1599590522-1256792510.1597065586
	if len(object.Signatures) != 1 {
		return nil, errors.New("Only one signature is allowed!")
	}

	if object.Signatures[0].Header.Algorithm != "HS256" {
		return nil, errors.New("Only HS256 is allowed as signing algorithm!")
	}

	output, err := object.Verify(&key)
	if err != nil {
		log.Println(err)
		return nil, err
	}

	return output, nil
}

func processRequest(r *http.Request) int {
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
		return http.StatusUnauthorized
	}

	// so here the request is verified, we are good to go
	resp, err := client.Post("http://localhost:10009", "text/json", bytes.NewReader(payload))
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
var privateKey string = os.Getenv("APC_PRIVATE_KEY")

func main() {
	log.SetOutput(&lumberjack.Logger{
		Filename: ".\\input-proxy.log",
		MaxSize:  100, // megabytes
		Compress: true,
	})

	// privateKey = "ZXhhbXBsZSBobWFjIGtleQ"
	privateKey = strings.TrimSpace(privateKey)
	if privateKey == "" {
		log.Fatal("Cannot retrieve private key from env.")
	}

	srv := &http.Server{
		Addr:         ":10017",
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
		Handler:      http.HandlerFunc(ServerHandler),
	}

	err := srv.ListenAndServe()
	if err != nil {
		log.Fatal(err) // we cannot run the server this, is fatal
	}
}

func ServerHandler(w http.ResponseWriter, r *http.Request) {
	// limit body size to something sensible https://stackoverflow.com/q/28282370/4807781
	r.Body = http.MaxBytesReader(w, r.Body, 100000)
	err := r.ParseForm()
	if err != nil {
		log.Println(err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	status := processRequest(r)
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
