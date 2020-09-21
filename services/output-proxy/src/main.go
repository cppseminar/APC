package main

import (
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"gopkg.in/natefinch/lumberjack.v2"
	"gopkg.in/square/go-jose.v2"
)

func sign(body []byte) (string, error) {
	// this we should load from environment
	var key jose.JSONWebKey
	key.UnmarshalJSON([]byte(`{
    "kty": "oct",
    "use": "sig",
    "k": "ZXhhbXBsZSBobWFjIGtleQ",
    "alg": "HS256"
	}`))

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
	if r.Method != "POST" {
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
		return http.StatusUnauthorized
	}

	// so here the request is verified, we are good to go
	resp, err := client.Post(sendTo, "text/json", strings.NewReader(payload))
	if err != nil {
		log.Println("Cannot forward request", err)
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
		Filename: ".\\output-proxy.log",
		MaxSize:  100, // megabytes
		Compress: true,
	})

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
