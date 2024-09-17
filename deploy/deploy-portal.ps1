# This script is responsible for deploying the whole solution. It is a wrapper 
# around bicep and helm deployments. It also takes care of some housekeeping 
# tasks like cleaning up orphaned role assignments.

# The script takes several parameters:
# - WHATIF: if set, the script will only simulate the deployment of bicep
# - PREFIX: prefix for all resources (default: apc)
# - LOCATION: location for the resource group (default: germanywestcentral)
# - DATA_RG: resource group where the data is stored (optional: $PREFIX-data)
# - REGISTRY: name of the container registry (optional: first found in $DATA_RG)
# - DNS_RG: resource group where the dns zone is stored (optional: $PREFIX-dns)
# - DNS_ZONE: name of the dns zone (optional: first found in $DNS_RG)

param (
    [switch]$WHATIF = $False,
    [string]$PREFIX = "apc",
    [string]$LOCATION = "germanywestcentral",
    [string]$DATA_RG = "",
    [string]$REGISTRY = "",
    [string]$DNS_RG = "",
    [string]$DNS_ZONE = ""
)

$GROUP = "$PREFIX-deployment"

if ($DATA_RG -eq "") {
    $DATA_RG = $PREFIX + "-data"
}

if ($DNS_RG -eq "") {
    $DNS_RG = $PREFIX + "-dns"
}

# if $REGISTRY is not set, and if there is only one registry in 
# provided resource group, we assume it is it
if ($REGISTRY -eq "") {
    # get count of acr in resource group so we can decide which to use
    $REGISTRIES = az acr list -g $DATA_RG | ConvertFrom-Json
    $REGISTRIES_COUNT = $REGISTRIES.Count
    if ($REGISTRIES_COUNT -eq 0) {
        Write-Output "No acr found in $DATA_RG"
        exit 1
    }
    if ($REGISTRIES_COUNT -gt 1) {
        Write-Output "More than one acr found in $DATA_RG, please specify"
        exit 1
    }

    $REGISTRY = $REGISTRIES[0].name

    Write-Output "Using registry $REGISTRY"
}

# if $DNS_ZONE is not set, and if there is only one dns zone in 
# provided resource group, we assume it is it
if ($DNS_ZONE -eq "") {
    # get count of dns zones in resource group so we can decide which to use
    $DNS_ZONES = az network dns zone list -g $DNS_RG | ConvertFrom-Json
    $ZONES_COUNT = $DNS_ZONES.Count
    if ($ZONES_COUNT -eq 0) {
        Write-Output "No dns zone found in $DNS_RG"
        exit 1
    }
    if ($ZONES_COUNT -gt 1) {
        Write-Output "More than one dns zone found in $DNS_RG, please specify"
        exit 1
    }

    $DNS_ZONE = $DNS_ZONES[0].name

    Write-Output "Using dns zone $DNS_ZONE"
}

# clean up orphaned role assignments by calling script
if ($WHATIF -eq $False) {
    ./bicep/cleanup-azure-roles.ps1 -ResourceGroupName $DATA_RG
}

# we do this mainly to run the deployment scoped in a resource group
# this way we are at least somewhat sure that we don't accidentally 
# break someting in another resource group
if ($WHATIF -eq $False) {
    az group create -n $GROUP -l $LOCATION
}

$bicepParams = @{
    "prefix"=$PREFIX
    "containerRegistry"=$REGISTRY
    "location"=$LOCATION
    "dnsResourceGroup"=$DNS_RG
    "dnsZoneName"=$DNS_ZONE
    "dataResourceGroup"=$DATA_RG
}

$bicepParamsStr = ($bicepParams.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join " "

$deploymentParams = "--resource-group $GROUP --template-file ./bicep/main.bicep --parameters $bicepParamsStr --mode Complete"

if ($WHATIF -eq $True) {
    Invoke-Expression "az deployment group what-if $deploymentParams"
    exit 0
}

$result = Invoke-Expression "az deployment group create $deploymentParams -n ""MainDeploy""" | ConvertFrom-Json

$public_ip_rg = $GROUP
$public_ip_name = $result.properties.outputs.portalIpName.value

$aks_name = $result.properties.outputs.aksName.value

# create temp file to serve as kubeconfig
$kubeconfig = [System.IO.Path]::GetTempFileName()
az aks get-credentials -g $GROUP -n $aks_name --file $kubeconfig

try {
    # now it is time to deploy helm charts
    helm upgrade --kubeconfig $kubeconfig --install $PREFIX ./helm `
        --set projectName=$PREFIX `
        --set environment=dev `
        --set dockerRepository=$REGISTRY.azurecr.io `
        --set websiteHost=$DNS_ZONE `
        --set LBinternal=10.14.254.254 `
        --set ingressIpName=$public_ip_name `
        --set ingressIpRg=$public_ip_rg

    # deploy rest of secrets
    kubectl apply -f ./helm/k8s/apc-secrets.yaml -n apc --kubeconfig $kubeconfig
} finally {
    # remove temporary kubeconfig
    Remove-Item $kubeconfig
}
