#!/bin/bash
PREFIX="apc"
GROUP="$PREFIX-deployment"
REGISTRY="$PREFIX-registry"

az group create -n "$GROUP" -l "germanywestcentral"

if [[ $# == 1 ]]; then
    az deployment group create -g "$GROUP" -f "./main.bicep" --parameters "prefix=$PREFIX" "containerRegistry=$REGISTRY" --mode Complete -n "MainDeploy"
else
    az deployment group what-if -g "$GROUP" -f "./main.bicep" --parameters "prefix=$PREFIX" --mode Complete
fi
