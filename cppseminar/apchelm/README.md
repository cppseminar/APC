# Deployment of kubernetes cluster

Everything can be installed with helm. Only secrets in folder `k8s` should be applied with `kubectl`.

## Mongo init script

Make sure config map in `./mongo/mongo-config.yaml` contain the same init script as in `../mongo/init-mongo.js`.

## Deploy using helm and kubectl

1. `cd` into this directory
2. Update values in `values.yaml`
3. `helm upgrade -i -f values.yaml apc .` where `apc` is the name of deployment.
4. Go into `k8s` directory and fill in the secrets.
5. `kubectl apply -f .\k8s\apc-secrets.yaml -n apc`

## Run db backup task

We have cron job for periodic backup task, so it may be a good idea to create initial db backup to see if it is working. 

`kubectl create job --from=cronjob/mongo-db-backup mongo-db-backup-manual-001 -n apc`

This command will create job `mongo-db-backup-manual-001` and run it immediatelly. 

# Updating operators

We use RabbitMQ and MongoDB Community operator. Those are not added as dependencies (that way we are not able to add them to namespace), nor do we force you to install them separatelly using helm. We have them inside `./crds/` folder and some parts are in `./templates/mongo/mongo-operator.yaml`. To update them your best bet is to install them using helm with `--dry-run` option and then copy the output to appropriate files. 