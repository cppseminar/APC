#!/bin/bash
PREFIX="apc"
GROUP="$PREFIX-logger"
DBPASS='dac240740d8b411221d9eed30fd6e5fe'
az group create -n "$GROUP" -l "germanywestcentral"

if [[ $# == 1 ]]; then
    az deployment group create -g "$GROUP" -f "./logger.bicep" --parameters "prefix=$PREFIX"  --mode Complete -n "aaa"
else
    az deployment group what-if   -g "$GROUP" -f "./logger.bicep" --parameters "prefix=$PREFIX" --mode Complete
fi
