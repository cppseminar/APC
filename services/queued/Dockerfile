FROM golang:1.20-alpine3.18 AS build

WORKDIR /app
COPY . .
ENV CGO_ENABLED=0
RUN go build -o queued cmd/queue/main.go

FROM alpine:3.18 AS dev

ARG DOCKER_REGISTRY_USER
ARG DOCKER_REGISTRY_PASS

WORKDIR /app

RUN echo '{ "dockerUsername":"'$DOCKER_REGISTRY_USER'", "dockerPassword":"'$DOCKER_REGISTRY_PASS'"}' > config.json
COPY --from=build /app/queued .

ENTRYPOINT ["./queued", "-config", "config.json", "-port", "10009"]
