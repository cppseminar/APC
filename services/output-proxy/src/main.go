package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"gopkg.in/square/go-jose.v2"
)

// key should be base64 encoded, without trailing '='
var privateKey string = os.Getenv("APC_PRIVATE_KEY")

var tr = &http.Transport{
	ResponseHeaderTimeout:  10 * time.Second,
	IdleConnTimeout:        30 * time.Second,
	MaxResponseHeaderBytes: 1024,
}

var client = &http.Client{Transport: tr}

func sign(body []byte) (string, error) {
	var key jose.JSONWebKey
	key.UnmarshalJSON([]byte(fmt.Sprintf(`{
    "kty": "oct",
    "use": "sig",
    "k": "%v",
    "alg": "HS256"
	}`, privateKey)))

	signer, err := jose.NewSigner(jose.SigningKey{Algorithm: jose.HS256, Key: key}, nil)
	if err != nil {
		log.Println(err)
		return "", err
	}

	object, err := signer.Sign(body)
	if err != nil {
		log.Println(err)
		return "", err
	}

	return object.CompactSerialize()
}

func processRequest(r *http.Request) int {

	if r.Method != "PATCH" {
		log.Println("Only post requests are supported!")
		return http.StatusBadRequest
	}

	sendTo := r.Header.Get("X-Send-To")
	if len(sendTo) == 0 {
		log.Println("X-Send-To not found in request header.")
		return http.StatusBadRequest
	}

	req, err := ioutil.ReadAll(r.Body)
	if err != nil {
		log.Println("Cannot read http body!")
		return http.StatusInternalServerError
	}

	payload, err := sign(req)
	if err != nil {
		return http.StatusInternalServerError
	}

	forwardReq, err := http.NewRequest("PATCH", sendTo, strings.NewReader(payload))
	forwardReq.Header.Set("Accept", "*/*")
	if err != nil {
		log.Println("Cannot create request", err)
		return http.StatusInternalServerError
	}

	resp, err := client.Do(forwardReq)
	if err != nil {
		log.Println("Cannot forward request", err)
		return http.StatusInternalServerError
	}

	// forward the error code
	return resp.StatusCode
}

func main() {
	log.Println("Output-proxy is starting")
	privateKey = strings.TrimSpace(privateKey)
	if privateKey == "" {
		log.Fatal("Cannot retrieve private key from env.")
	}

	srv := &http.Server{
		Addr:         ":10018",
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
	w.WriteHeader(processRequest(r))
}
