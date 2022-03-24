#!/bin/zsh
PREFIX="apc2"
GROUP="$PREFIX-deployment"
az group create -n "$GROUP" -l "germanywestcentral"
az deployment group create -g "$GROUP" -f "./main.bicep" --parameters "prefix=$PREFIX"
