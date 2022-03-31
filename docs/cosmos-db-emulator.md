# Cosmos DB Emulator on Linux Docker

Microsoft provide emulator for Linux, but is is kind of weird working. Here I provide some details and workarounds. In the end we do not use it, but at least it can be useful in the future.

## Running in docker compose

```yaml
services:
    cosmosdb.local:
        image: mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator
        mem_limit: 3GB
        cpu_count: 2
        hostname: cosmosdb
        ports:
            - 8081:8081
            - 10251:10251
            - 10252:10252
            - 10253:10253
            - 10254:10254
        environment:
            AZURE_COSMOS_EMULATOR_PARTITION_COUNT: 16
            AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE: 'true'
            AZURE_COSMOS_EMULATOR_IP_ADDRESS_OVERRIDE: 10.0.0.246
            AZURE_COSMOS_EMULATOR_CERTIFICATE: /usr/local/share/ca-certificates/cosmosdb-emulator.pfx
#AccountEndpoint=https://10.0.0.246:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
        networks:
            sharednet:
                ipv4_address: 10.0.0.246
        volumes:
            - cosmosdb_data:/tmp/cosmos # weird, this may change in the future
            - ./cosmos-db-emul/cosmosdb-emulator.pfx:/usr/local/share/ca-certificates/cosmosdb-emulator.pfx

networks:
    sharednet:
        external: false
        ipam:
            driver: default
            config:
                - subnet: 10.0.0.0/24
volumes:
    cosmosdb_data:

```

### Image

Image is provided by Microsoft. It seems like currently they only support `latest` tag. But from testing it do in fact looks like they have the latest cosmos db emulator there inside the image are windows binaries that are run with some kind of emulator `runpal`.

### Resources

Microsoft recommends 3GB of memory and 2 CPU. From my testing it do not make any difference to use 6 CPU or 1 CPU.

### Ports

You can see the ports used by emulator <https://docs.microsoft.com/en-us/azure/cosmos-db/emulator-command-line-parameters>.

### Network

Since it seems like you need to provide the IP address to the container and it is in the certificate it make sense to statically assign IP address to the container.

### Volumes

You need one volume to store persistent data. The trick here is, that the path it not really documented to my knowledge. From inspecting the container I concluded, that `/tmp/cosmos` is used to store data. It seems weird, but there is no way to override this path. So the persistent volume must be mapped to this path. Other useful detail is to provide the same certificate every time the container run. This can be done by first exporting the certificate from filesystem (emulator will create it) `/tmp/cosmos/appdata/default.sslcert.pfx` and than mapping it to the filesystem.

### Environment

* *AZURE_COSMOS_EMULATOR_PARTITION_COUNT* partition count, not sure exactly what this is, but if lower it will run faster.
* *AZURE_COSMOS_EMULATOR_ENABLE_DATA_PERSISTENCE* should be true if you want to persist the data, otherwise emulator will wipe it on startup
* *AZURE_COSMOS_EMULATOR_IP_ADDRESS_OVERRIDE* documentation said this is important to set up.
* *AZURE_COSMOS_EMULATOR_CERTIFICATE* this is nor really documented, but it is obvious from startup script, that you can set it to cert path and emulator will use that one, instead of creating new one.

## Certificate

You can go to `http://localhost:8081/_explorer/emulator.pem` to download the cert. You can than copy it to docker of your choice and run some commands to trust it.

```docker
COPY "cosmosdb-emulator.pem" "/usr/local/share/ca-certificates/cosmosdb-emulator.crt"
RUN update-ca-certificates
```

From C# connection should work with the cert imported. But from PYthon it will not and seems like the easiest way to do it there is to disable cert validation. Just set `connection_verify` to `False`.

## Conclusion

**Why don't we use it?**

First of all it starts like 30 seconds. But the may dealbreaker was the fact you need to run it several times, since it even start to work and then it sometimes fails to respond in 65seconds. Which results in timeout. It really annoys me.
