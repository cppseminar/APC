FROM golang:1.20-alpine3.18 AS build

WORKDIR /app
COPY . .
ENV CGO_ENABLED=0
RUN go build -o queued cmd/queue/main.go

FROM alpine:3.18 AS dev

WORKDIR /app
COPY --from=build /app/queued .
COPY config.json .

ENTRYPOINT ["./queued", "-config", "config.json", "-port", "10009"]
