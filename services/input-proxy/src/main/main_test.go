package main

import (
	"bytes"
	"fmt"
	"gopkg.in/square/go-jose.v2"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"testing"
	"time"
)

func TestGetSignKey(t *testing.T) {
	defer os.Setenv(envPrivateKey, os.Getenv(envPrivateKey))

	os.Setenv(envPrivateKey, "")
	t.Run("Empty", func(t *testing.T) {
		_, err := getSigningKey()
		if err == nil {
			t.Fail()
		}
	})

	os.Setenv(envPrivateKey, " ae==   ")
	t.Run("Padding2", func(t *testing.T) {
		result, err := getSigningKey()
		if err != nil {
			t.Fail()
		}
		if result != "ae" {
			t.Fail()
		}
	})

	os.Setenv(envPrivateKey, " ZS4=  ")
	t.Run("Padding1", func(t *testing.T) {
		result, err := getSigningKey()
		if err != nil {
			t.Fail()
		}
		if result != "ZS4" {
			t.Fail()
		}
	})

	os.Setenv(envPrivateKey, " c3Vy  ")
	t.Run("No padding", func(t *testing.T) {
		result, err := getSigningKey()
		if err != nil {
			t.Fail()
		}
		if result != "c3Vy" {
			t.Fail()
		}
	})

	os.Setenv(envPrivateKey, "+.++")
	t.Run("Invalid", func(t *testing.T) {
		_, err := getSigningKey()
		if err == nil {
			t.Fail()
		}
	})

}

func TestBuildForwardUrl(t *testing.T) {

	oldUrl := url.URL{
		Host: "localhost:1234",
		Path: "/some/file",
	}

	result := buildForwardURL(false, "queue:1234", oldUrl)

	if result != "http://queue:1234/some/file" {
		t.Error("Bad format of url")
	}

}

// Function from output proxy to sign json
func sign(body []byte, privateKey string) ([]byte, error) {
	var key jose.JSONWebKey
	key.UnmarshalJSON([]byte(fmt.Sprintf(`{
    "kty": "oct",
    "use": "sig",
    "k": "%v",
    "alg": "HS256"
	}`, privateKey)))

	signer, err := jose.NewSigner(jose.SigningKey{Algorithm: jose.HS256, Key: key}, nil)
	if err != nil {
		return nil, err
	}

	object, err := signer.Sign(body)
	if err != nil {
		return nil, err
	}

	s, err := object.CompactSerialize()
	return []byte(s), err
}

func buildRequest(body []byte, uri string, key string) http.Request {

	body, err := sign(body, key)
	if err != nil {
		panic("Test signer error")
	}



	var request = http.Request{
		Body: ioutil.NopCloser(bytes.NewReader(body)),
		URL: &(url.URL{
			Path: uri,
		}),
	}

	return request
}

func TestVerifyExtract(t *testing.T) {
	const key string = "aaaa"

	const messageFmt = `
	{
		"timestamp": %v,
		"uri": "/api/abcd/",
		"payload": { "aa" : "bb"}
	}
	`
	const messageFmt1 = `
	{
		"timestamp": %v,
		"uri": "/api/abcd/",
		"payload": ""
	}
	`

	const messageFmt2 = `
	{
		"timestamp": %v,
		"uri": "/api/abcd/",
		"payload": { "aa" : "bb"},
		"additional" : 1
	}
	`

	const messageFmt3 = `
	{
		"timestamp": %v,
		"uri": "/api/abcd/"
	}
	`

	t.Run("Correct", func(t *testing.T) {
		var message []byte = []byte(fmt.Sprintf(messageFmt, time.Now().Unix()))
		request := buildRequest(message, "/api/abcd/", key)

		if payload, err := verifyAndExtract(&request, key); err != nil {
			t.Error(err)
		} else {
			if string(payload) != `{"aa":"bb"}` {
				t.Errorf("Bad payload %v", string(payload))
			}
		}
	})

	t.Run("Old timestamp", func(t *testing.T) {
		var message = []byte(fmt.Sprintf(messageFmt, time.Now().Unix()-11))
		request := buildRequest(message, "/api/abcd/", key)
		if _, err := verifyAndExtract(&request, key); err == nil {
			t.Error("Should fail")
		}
	})

	t.Run("Bad signature", func(t *testing.T) {
		var message = []byte(fmt.Sprintf(messageFmt, time.Now().Unix()))
		request := buildRequest(message, "/api/abcd/", "wwww")
		if _, err := verifyAndExtract(&request, key); err == nil {
			t.Error("Should fail")
		}
	})

	t.Run("More fields", func(t *testing.T) {
		var message = []byte(fmt.Sprintf(messageFmt2, time.Now().Unix()))
		request := buildRequest(message, "/api/abcd/", key)
		if _, err := verifyAndExtract(&request, key); err == nil {
			t.Error("Should fail")
		}
	})

	t.Run("Missing payload", func(t *testing.T) {
		var message = []byte(fmt.Sprintf(messageFmt3, time.Now().Unix()))
		request := buildRequest(message, "/api/abcd/", key)
		if _, err := verifyAndExtract(&request, key); err == nil {
			t.Error("Should fail")
		}
	})

	t.Run("Empty payload", func(t *testing.T) {
		var message = []byte(fmt.Sprintf(messageFmt1, time.Now().Unix()))
		request := buildRequest(message, "/api/abcd/", key)
		payload, err := verifyAndExtract(&request, key)
		if err != nil {
			t.Errorf("Shouldn't fail %v", err)
		}
		if string(payload) != `""` {
			t.Errorf("Expected \"\" got %v", string(payload))
		}
	})

	t.Run("Bad URI", func(t *testing.T) {
		var message = []byte(fmt.Sprintf(messageFmt3, time.Now().Unix()))
		request := buildRequest(message, "/api/abcd/es", key)
		if _, err := verifyAndExtract(&request, key); err == nil {
			t.Error("Should fail")
		}
	})

}
