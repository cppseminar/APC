// go get github.com/xeipuuv/gojsonschema

package main

import (
	"errors"
	"io/ioutil"
	"log"
	"net/http"
	"time"

	"github.com/xeipuuv/gojsonschema"
	"gopkg.in/square/go-jose.v2"
)

func getSchema() *gojsonschema.Schema {
	dat, err := ioutil.ReadFile("./schema.json")
	if err != nil {
		log.Fatal(err)
	}

	schemaLoader := gojsonschema.NewBytesLoader(dat)

	schema, err := gojsonschema.NewSchema(schemaLoader)
	if err != nil {
		log.Fatal(err)
	}

	return schema
}

func verifyJWSAndExtractPayload(body []byte) ([]byte, error) {
	object, err := jose.ParseSigned(string(body))
	if err != nil {
		log.Println("Cannot parse body as JWS '", string(body), "'.", err)
		return nil, err
	}

	// this we should load from environment
	var publicKey jose.JSONWebKey
	publicKey.UnmarshalJSON([]byte(`{
    "kty":"EC",
    "crv":"P-256",
    "x":"bWrIDOM1ZD_aeQ--HJoqL_ench7qRSGBCD_5t3gBgzM",
    "y":"BJKB0iiarWhW1Q_btd2KSBIwYSGfn38T2xKq36fH-Ks"
	}`))

	// i'm kind of scared from jose, so I add here those paranoid checks
	// https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/?_ga=2.1739384.896580470.1599590522-1256792510.1597065586
	if len(object.Signatures) != 1 {
		return nil, errors.New("Only one signature is allowed!")
	}

	if object.Signatures[0].Header.Algorithm != "ES256" {
		return nil, errors.New("Only ES256 is allowed as signing algorithm!")
	}

	output, err := object.Verify(&publicKey)
	if err != nil {
		log.Println("Invalid signature '", string(body), "'.", err)
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
		log.Println("Cannot read http body!")
		return http.StatusInternalServerError
	}

	payload, err := verifyJWSAndExtractPayload(req)
	if err != nil {
		return http.StatusUnauthorized
	}

	// check payload against json scheme to validate it
	jsonDocument := gojsonschema.NewBytesLoader(payload)

	result, err := schema.Validate(jsonDocument)
	if err != nil {
		log.Println(err)
		return http.StatusBadRequest
	}

	if !result.Valid() {
		log.Println(result.Errors())
		return http.StatusBadRequest
	}

	// so here the request is verified and validated, we are good to go

	return http.StatusOK
}

var schema *gojsonschema.Schema

func main() {
	schema = getSchema()

	srv := &http.Server{
		Addr:         ":1488",
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
	status := processRequest(r)
	if status != http.StatusOK {
		log.Println("Request",
			r.Method,
			r.Host,
			r.Proto,
			"remote addr", r.RemoteAddr,
			"x-real-ip", r.Header.Get("X-Real-Ip"),
			"x-forwarded-for", r.Header.Get("X-Forwarded-For"),
			"ended up with status", status)
	}

	w.WriteHeader(status)
}
