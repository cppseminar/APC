#!/bin/bash

set -euxo pipefail

apt-get update

apt-get -y install subversion

svn checkout https://github.com/cppseminar/APC/trunk/services ./queued

# call install, parameters are docker credentials (username, password)
chmod +x ~/queued/scripts/install.sh
( cd ~/queued/scripts && exec ./install.sh $1 $2 $3 )