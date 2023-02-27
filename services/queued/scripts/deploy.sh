#!/bin/bash

set -euo pipefail
{ set +x; } 2>/dev/null

git clone https://github.com/cppseminar/APC.git --depth=1

mv ./APC/services/queued ./queued
rm -r ./APC

if [ "$#" -ne 1 ]; then
    CONFIG=`mktemp`
    echo "{ }" > $CONFIG
else
    CONFIG=`realpath "$1"`
fi


# call install
chmod +x ./queued/scripts/install.sh
( cd ./queued/scripts && exec ./install.sh $CONFIG)
