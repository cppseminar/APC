#!/bin/bash

apt-get update

apt-get -y install svn

svn checkout https://github.com/cppseminar/APC/trunk/services ~/queued

# call install, parameters are docker credentials (username, password)
chmod +x ~/queued/scripts/install.sh
( ~/queued/scripts/install.sh $1 $2 $3 )