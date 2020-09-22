FROM golang:1.15.2-buster
COPY src /src
WORKDIR /src
RUN go build
ENTRYPOINT ["/src/input-proxy"]
