package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"

	"gopkg.in/square/go-jose.v2"
)

// Format of requests, which are accepted by this proxy
type proxyRequest struct {
	Timestamp int64       `json:"timestamp"`
	URI       *string     `json:"uri"`
	Payload   interface{} `json:"payload"`
}

func verifyJWSAndGetBody(body []byte, privateKey string) ([]byte, error) {
	object, err := jose.ParseSigned(string(body))
	if err != nil {
		log.Println("Cannot parse body as JWS '", string(body), "'.")
		return nil, err
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

var client = &http.Client{Transport: tr}

// Checks signature, timestamp and request uri. Returns payload from message
func verifyAndExtract(request *http.Request, signingKey string) ([]byte, error) {
	body, err := ioutil.ReadAll(request.Body)
	if err != nil {
		return nil, err
	}

	jwsContent, err := verifyJWSAndGetBody(body, signingKey)
	if err != nil {
		return nil, err
	}
	// It is signed. Now let's verify uri and timestamp
	var parsedRequest proxyRequest

	decoder := json.NewDecoder(bytes.NewReader(jwsContent))
	decoder.DisallowUnknownFields()

	if err = decoder.Decode(&parsedRequest); err != nil {
		return nil, err
	}

	var currentTime int64 = time.Now().Unix()

	// We are accepting dates from future, this is because in development there
	// were situations, when this shit happened.  Idk about prod machines, but
	// I hope it's fine
	if parsedRequest.Timestamp+10 < currentTime || parsedRequest.Timestamp > currentTime+1 {
		return nil, fmt.Errorf("Invalid (expired?) timestamp %v current %v",
			parsedRequest.Timestamp,
			currentTime,
		)
	}

	// So we are kinda good here with timestamp. Now let's check, if requested
	// uri is same as the one in json

	if request.URL == nil {
		return nil, errors.New("Empty request url")
	}

	if parsedRequest.URI == nil {
		return nil, errors.New("Missing uri in json")
	}

	if *parsedRequest.URI != request.URL.Path {
		return nil, fmt.Errorf("Uris don't match '%s' '%s'",
			*parsedRequest.URI,
			request.URL.Path)
	}

	// And let's check if payload is actually present
	forwardData, err := json.Marshal(parsedRequest.Payload)
	if err != nil {
		return nil, err
	}
	if parsedRequest.Payload == nil {
		return nil, errors.New("Empty payload field")
	}

	return forwardData, nil
}
