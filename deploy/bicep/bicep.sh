#!/bin/zsh
PREFIX="apc"
GROUP="$PREFIX-deployment"
az group create -n "$GROUP" -l "germanywestcentral"

if [[ $# == 1 ]]; then
    az deployment group create -g "$GROUP" -f "./logger.bicep" --parameters "prefix=$PREFIX" --mode Complete
else
    az deployment group what-if   -g "$GROUP" -f "./logger.bicep" --parameters "prefix=$PREFIX" --mode Complete
fi
