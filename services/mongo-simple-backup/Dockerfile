FROM alpine:3.18 AS get_rclone

RUN apk add curl \
    && curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip \
    && unzip rclone-current-linux-amd64.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin/ \
    && chmod 755 /usr/bin/rclone

FROM golang:1.20-alpine3.18 AS build_mongodump

WORKDIR /build

RUN apk update \
    && apk add git \
    && apk add gcc \
    && apk add musl-dev \
    && apk add krb5-dev \
    && git clone https://github.com/mongodb/mongo-tools \
    && cd mongo-tools \
    && ./make build -pkgs=mongodump

FROM alpine:3.18 AS build

WORKDIR /tools

COPY . .
COPY --from=get_rclone /usr/bin/rclone /usr/bin/rclone
COPY --from=build_mongodump /build/mongo-tools/bin/mongodump /usr/bin/mongodump

RUN mkdir /var/dumps \
    && echo "#!/bin/sh" > ./dump.sh \
    && echo "/tools/backup.sh --url \${MONGO_CONN_STR} --output /var/dumps" >> ./dump.sh \
    && echo "rclone move /var/dumps MONGO_BACKUPS:/mongo-db-dumps --use-json-log" >> ./dump.sh \
    && chmod 0766 ./dump.sh \
    && chmod 0766 ./backup.sh \
    && mkdir -p /root/.config/rclone \
    && touch /root/.config/rclone/rclone.conf \
    && apk add krb5-libs

FROM build AS dev

RUN mv ./dump.sh /etc/periodic/15min/dump.sh
CMD crond -f -l 8

FROM build AS final

CMD ./dump.sh
