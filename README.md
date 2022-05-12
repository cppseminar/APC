# Apc portal

## Development

To successfully run portal locally, you need to have docker installed (on Windows it can be Docker Desktop) and access to some kind of virtual machine (for example Hyper-V) with Linux running. Make sure you can access the VM and the VM can access the host (on Windows Hyper-V adapters are part of the Unidentified networks, so they are treated as public, so some FW rules are needed).

### Create google app

Go to <https://console.cloud.google.com/apis/credentials/> and create new app. Set

* Authorized Javascript origins to `http://localhost:8080`
* Authorized redirect URIs to `http://localhost:8080/signin-google`

Keep the client id and secret you will need them.

### Provision tester VM

After you create new Linux machine.

1. Copy file `./services/queued/scripts/deploy.sh`.
2. Create new configuration file (for example `config.json`) where you put two values `dockerUsername` and `dockerPassword`. Those shoud be username and password of docker repository where are the images to run tests. This is probably the only part where you need some kind of external service. Also make sure the repository is reachable.
3. Run `./deploy.sh config.json`.
4. If everything runs ok, you should see that the `queued` service is running.

### Run all services

1. Copy cosmos db certificate from `./cppseminar/cosmosdb-emul/emulator.pem` to both `./cppseminar/submissions` and `./cppseminar/testservice`.
2. Go to `./cppseminar` and run `docker compose up` you need to have few environment variables present (e.g. create `.env` file there or just set them)
   * `COSMOS_CONN_STR=AccountEndpoint=https://172.19.0.100:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==` (this is set to local cosmos db emulator, it is present, because sometimes the emulator just won't run in that case you can replace it to actual cosmos instance)
   * `GOOGLE_CLIENT_ID` google client id
   * `GOOGLE_CLIENT_SECRET` google client secret
   * `VM_TEST_ADDR_PORT` address of VM where tester will run with port (be default it is `10009`), for example `172.23.193.24:10009`
   * `VM_TEST_RETURN_ADDR` ip address where `vmtestserver` can be reached, it is probably the ip of host of the vm in previous env, for example `172.23.193.1`
3. After everything has started go to <http://localhost:8080/> and you are good to go.
