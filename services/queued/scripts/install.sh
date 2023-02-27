#!/bin/bash

set -euo pipefail
{ set +x; } 2>/dev/null

# build the service
docker build --target build -t queued-builder ..
id=$(docker create queued-builder)
docker cp $id:/app/queued /usr/local/bin/queued
docker rm -v $id

chmod +x /usr/local/bin/queued

# copy config file
cp ./queued.service.ini /etc/systemd/system/queued.service
chmod 644 /etc/systemd/system/queued.service

cp $1 /usr/local/etc/queued.conf.json

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
