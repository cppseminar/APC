// go get github.com/xeipuuv/gojsonschema

package main

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"time"

	"github.com/xeipuuv/gojsonschema"
)

type RequestMessage struct {
	ReturnUrl   string
	DockerImage string
	Files       map[string]string
	MaxRunTime  int
}

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

var schema *gojsonschema.Schema

func main() {
	schema = getSchema()

	srv := &http.Server{
		Addr:         ":10009",
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

func processRequest(r *http.Request) int {
	if r.Method != "POST" {
		return http.StatusBadRequest
	}

	req, err := ioutil.ReadAll(r.Body)
	if err != nil {
		return http.StatusInternalServerError
	}

	// check payload against json scheme to validate it
	jsonDocument := gojsonschema.NewBytesLoader(req)

	result, err := schema.Validate(jsonDocument)
	if err != nil {
		log.Println(err)
		return http.StatusBadRequest
	}

	if !result.Valid() {
		log.Println(result.Errors())
		return http.StatusBadRequest
	}

	// so here the request is validated, we are good to go
	var msg RequestMessage
	if err := json.Unmarshal(req, &msg); err != nil {
		log.Println(err)
		return http.StatusBadRequest
	}

	return http.StatusOK
}

func ServerHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(processRequest(r))
}
