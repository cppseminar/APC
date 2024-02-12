# Apc portal

[![Build microservices](https://github.com/cppseminar/APC/actions/workflows/publish-microservices.yaml/badge.svg)](https://github.com/cppseminar/APC/actions/workflows/publish-microservices.yaml)

## Development

To successfully run portal locally, you need to have docker installed (on Windows it can be Docker Desktop).

### Create google app

Go to <https://console.cloud.google.com/apis/credentials/> and create new app. Set

* Authorized Javascript origins to `http://localhost:8080`
* Authorized redirect URIs to `http://localhost:8080/signin-google`

Keep the client id and secret you will need them.

### Create azure blob storage account

Currently we do not support azurite for mongo backups, so if you want that you need actual azure storage. If you are good without it just, remove service `mongo-backup.local` from `docker-compose.yml` file in folder `cppseminar`.

### Run all services

1. Go to `./cppseminar` and run `docker compose up` you need to have few environment variables present (e.g. create `.env` file there or just set them)
   * `GOOGLE_CLIENT_ID` google client id
   * `GOOGLE_CLIENT_SECRET` google client secret
   * `STORAGE_AZUREBLOB_ACCOUNT` and `STORAGE_AZUREBLOB_KEY` those are azure blob storage account for backups, so this is optional if you do not want that.
   * `DOCKER_REGISTRY_USER` and `DOCKER_REGISTRY_PASS` are credential for login to docker repository, this is the repository where test images are present
2. After everything has started go to <http://localhost:8080/> and you are good to go.

## Deployment

We have production Kubernetes [deployment](./cppseminar/apchelm/README.md) in folder `cppseminar/apchelm`.
