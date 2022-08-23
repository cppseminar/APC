# Deployment of kubernetes cluster

Everything can be installed with helm. Only secrets in folder `k8s` should be applied with `kubectl`.

## Mongo init script

Make sure config map in `./mongo/mongo-config.yaml` contain the same init script as in `../mongo/init-mongo.js`.

## Assing one node for running DB

This is necessary to prevent data loss, we do not really have some resiliant mongo cluster, so this is a cheap solution to our problem. Mongo will run on the selected node and no other. It should alwas get the same node when restarted. It can be problematic upon node restart, kubernetes really do not care what happen to the label, so in that case you need to relabel the node.  

1. `kubectl get nodes` and pick one node
2. `kubectl label nodes NODE app=database` to mark one node for database, this is needed because we use simple host path as persistent storage provider and we need to make sure it is always in the same node. 
3. You can use `kubectl get nodes --show-labels` to see whether you have it all set. 

## dockerconfigjson

`kubectl create secret docker-registry container-registry --docker-server=<your-registry-server> --docker-username=<your-username> --docker-password=<your-password> --docker-email=<your-email>`

`<your-registry-server>` should be the same as `dockerRepository` in `values.yaml`.

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

# Running in minikube

You need to add following lines in `./templates/rabbitmq/apc-rabbitmq.yaml`. It is because on minikube there are some problems with privileges in mounted volumes.

```yaml
  override:
    statefulSet:
      spec:
        template:
          spec:
            containers: []
            securityContext: {}
            initContainers:
            - name: setup-container
              securityContext: {}
```