FROM golang:1.15.2-buster
COPY src /src
WORKDIR /src
RUN go build -o input-proxy.exe ./main/
ENTRYPOINT ["/src/input-proxy.exe", "--port", "10017", "--url", "http://localhost:10009"]
