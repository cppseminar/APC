# Deployment of kubernetes cluster

Everything can be installed with helm. Only secrets in folder `k8s` should be applied with `kubectl`. 

## dockerconfigjson

You can either uncomment the part in `values.yaml` and provide docker auth credentials, or you can leave it commented and use `kubectl` to install the secret. 

`kubectl create secret docker-registry container-registry --docker-server=<your-registry-server> --docker-username=<your-name> --docker-password=<your-pword> --docker-email=<your-email>`

`<your-registry-server>` should be the same as `dockerRepository` in `values.yaml`.