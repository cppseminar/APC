package main

import (
	"os"
	"testing"
)

func TestGetSignKey(t *testing.T) {
	defer os.Setenv(envPrivateKey, os.Getenv(envPrivateKey))

	os.Setenv(envPrivateKey, "")
	t.Run("Empty", func(t *testing.T) {
		_, err := getSigningKey()
		if err != nil {
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
