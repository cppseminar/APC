
param location string = 'germanywestcentral'

@minLength(1)
@maxLength(5)
param prefix string

param dataResourceGroup string
param containerRegistry string

param dnsResourceGroup string
param dnsZoneName string

module network 'modules/mainnet.bicep' = {
  name: '${prefix}-vnet-deploy'
  params: {
    location: location
    prefix: prefix
  }
}

module compute 'modules/aks.bicep' = {
  name: '${prefix}-aks-deploy'
  params: {
    location: location
    prefix: prefix
    vnetName: network.outputs.vnetName
    subnetName: network.outputs.aksSubnetName
    dataResourceGroup: dataResourceGroup
    registryName: containerRegistry
  }
}

module ssset 'modules/scaleset.bicep' = {
  name: '${prefix}-sset-deploy'
  params: {
    location: location
    prefix: prefix
    lbSubnet: network.outputs.lbSubnet
    lbIp: network.outputs.lbIp
    ssSubnet: network.outputs.ssetSubnet
    dataResourceGroup: dataResourceGroup
    containerRegistry: containerRegistry
  }
}

module netAp 'modules/ap.bicep' = {
  name: '${prefix}-netap-deploy'
  params: {
    location: location
    vmSubnet: network.outputs.vmSubnet
    prefix: prefix
    vmIp: network.outputs.vmIp
  }
}

module dnsNetAp 'modules/dns-add.bicep' = {
  name: '${prefix}-dns-update-netap'
  scope: resourceGroup(dnsResourceGroup)
  params: {
    ipAddress: netAp.outputs.netApIp
    resourceName: dnsZoneName
    subDomain: 'netap'
  }
}

module dnsAks 'modules/dns-add.bicep' = {
  name: '${prefix}-dns-update-aks'
  scope: resourceGroup(dnsResourceGroup)
  params: {
    ipAddress: compute.outputs.publicIp
    resourceName: dnsZoneName
    subDomain: '@'
  }
}

output portalIpName string = compute.outputs.publicIpName
output aksName string = compute.outputs.aksName
