FROM golang:1.15.2-buster
COPY src /src
WORKDIR /src
RUN go build -o queue.exe ./main/
ENTRYPOINT ["/src/queue.exe"]
