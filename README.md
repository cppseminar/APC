# Apc portal

[![Build microservices](https://github.com/cppseminar/APC/actions/workflows/publish-microservices.yaml/badge.svg)](https://github.com/cppseminar/APC/actions/workflows/publish-microservices.yaml)

## Development

To successfully run portal locally, you need to have docker installed (on Windows it can be Docker Desktop).

### Create google app

Go to <https://console.cloud.google.com/apis/credentials/> and create new app. Set

* Authorized Javascript origins to `http://localhost:8080`
* Authorized redirect URIs to `http://localhost:8080/signin-google`

Keep the client id and secret you will need them.

### Run all services

1. Go to `./cppseminar` and run `docker compose up` you need to have few environment variables present (e.g. create `.env` file there or just set them)
   * `GOOGLE_CLIENT_ID` google client id
   * `GOOGLE_CLIENT_SECRET` google client secret
   * `DOCKER_REGISTRY_USER` and `DOCKER_REGISTRY_PASS` are credential for login to docker repository, this is the repository where test images are present
2. After everything has started go to <http://localhost:8080/> and you are good to go.

### Usefull URLs

* <http://localhost:8080/> - main page
* <http://localhost:9090> - mongo express, user `mexpress`, password `mexpress`
* <http://localhost:9901/> - envoy proxy admin page
* <http://azurite:10000/azuriteuser> - azurite blob storage, `AccountName=azuriteuser;AccountKey=UGFzc3dvcmQxMjMhfg==`, you can use [Azure Storage Explorer](https://azure.microsoft.com/en-us/features/storage-explorer/) to connect to it


## Deployment

We have production Kubernetes [deployment](./deploy/README.md) in folder `deploy`.
