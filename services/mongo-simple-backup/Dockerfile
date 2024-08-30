FROM golang:1.23.0-alpine3.20 AS build_mongodump

WORKDIR /build

RUN apk update \
    && apk add git \
    && apk add gcc \
    && apk add musl-dev \
    && apk add krb5-dev \
    && git clone https://github.com/mongodb/mongo-tools \
    && cd mongo-tools \
    && ./make build -pkgs=mongodump

FROM python:3.12-alpine3.20 AS build

WORKDIR /tools

COPY . .
COPY --from=build_mongodump /build/mongo-tools/bin/mongodump /usr/bin/mongodump

RUN mkdir /var/dumps \
    && chmod 0766 ./backup.sh \
    && chmod 0766 ./run.sh \
    && apk add krb5-libs \
    && apk add curl \
    && pip install azure-storage-blob

FROM build AS dev

RUN mv ./run.sh /etc/periodic/15min/run.sh
CMD crond -f -l 8

FROM build AS final

CMD ./run.sh
