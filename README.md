# Apc portal

[![Build microservices](https://github.com/cppseminar/APC/actions/workflows/publish-microservices.yaml/badge.svg)](https://github.com/cppseminar/APC/actions/workflows/publish-microservices.yaml)

## Development

To successfully run portal locally, you need to have docker installed (on Windows it can be Docker Desktop) and access to some kind of virtual machine (for example Hyper-V) with Linux running. Make sure you can access the VM and the VM can access the host (on Windows Hyper-V adapters are part of the Unidentified networks, so they are treated as public, so some FW rules are needed).

### Create google app

Go to <https://console.cloud.google.com/apis/credentials/> and create new app. Set

* Authorized Javascript origins to `http://localhost:8080`
* Authorized redirect URIs to `http://localhost:8080/signin-google`

Keep the client id and secret you will need them.

### Create config for worker

1. Go to `/services/queued/`.
2. Create new configuration file `config.json` (it is added in `.gitignore` so don't worry about accidental secrets leak) where you put two values `dockerUsername` and `dockerPassword`. Those shoud be username and password of docker repository where are the images to run tests. This is probably the only part where you need some kind of external service. Also make sure the repository is reachable.

### Create CosmosDB account 

Go to azure portal and create some CosmosDB account (for me serverless is working better).

### Run all services

1. Go to `./cppseminar` and run `docker compose up` you need to have few environment variables present (e.g. create `.env` file there or just set them)
   * `COSMOS_CONN_STR` connection string of Cosmos DB
   * `GOOGLE_CLIENT_ID` google client id
   * `GOOGLE_CLIENT_SECRET` google client secret
2. After everything has started go to <http://localhost:8080/> and you are good to go.
