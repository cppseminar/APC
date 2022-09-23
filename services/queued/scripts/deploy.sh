#!/bin/bash

set -euo pipefail
{ set +x; } 2>/dev/null

if [ $# -ne 1 ]; then
    echo "Illegal number of parameters" >&2
    echo "Usage:" $0 "conf_file" >&2
    echo -e "\tconf_file json with username and password to docker registry" >&2
    exit 2
fi

if [ ! -f "$1"  ]; then
    echo "$1 do not exists." >&2
    exit 2
fi

apt-get update

apt-get -y install subversion

svn checkout https://github.com/cppseminar/APC/trunk/services/queued ./queued

config=`realpath "$1"`

# call install
chmod +x ./queued/scripts/install.sh
( cd ./queued/scripts && exec ./install.sh $config )
