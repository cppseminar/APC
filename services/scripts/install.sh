#!/bin/bash

set -euxo pipefail

if [ $# -ne 3 ]; then
    echo "Illegal number of parameters" >&2
    echo "Usage:" $0 "repo user pass" >&2
    echo -e "\trepo docker repository" >&2
    echo -e "\tuser docker username" >&2
    echo -e "\tpass docker password" >&2
    exit 2
fi

# remove old docker packages
apt-get -y remove docker docker-engine docker.io containerd runc

apt-get update

apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# add official Docker key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --yes --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# use stable repository
echo \
    "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list

# install docker
apt-get -y install docker-ce docker-ce-cli containerd.io

# login to docker repository
docker login $1 -u $2 -p $3

# get go compiler
apt-get -y install golang-go

# build the service
go build -o /usr/local/bin/queued ../cmd/queue
chmod +x /usr/local/bin/queued

# copy config file
MY_PATH=$(readlink -f ./queued.service.ini)
echo "$MY_PATH"
cp ./queued.service.ini /etc/systemd/system/queued.service
chmod 644 /etc/systemd/system/queued.service

# reload units
systemctl daemon-reload

# start it and make it run on boot
if systemctl is-active --quiet queued; then
    systemctl restart queued
else
    systemctl start queued
fi

systemctl enable queued
systemctl status queued
