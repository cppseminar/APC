
param location string = 'westeurope'

@minLength(1)
@maxLength(5)
param prefix string

param dataResourceGroup string
param containerRegistry string

param dnsResourceGroup string
param dnsZoneName string

@description('Tags to apply to main network, in json format')
param networkTags string

module network 'modules/mainnet.bicep' = {
  name: '${prefix}-vnet-deploy'
  params: {
    location: location
    prefix: prefix
    tags: json(networkTags)
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
    podsIpRange: network.outputs.aksPodsIpRange
  }
}

module testers 'modules/testers.bicep' = {
  name: '${prefix}-testers-deploy'
  params: {
    location: location
    prefix: prefix
    lbSubnet: network.outputs.lbSubnet
    lbIp: network.outputs.lbIp
    ssSubnet: network.outputs.testersSubnet
    dataResourceGroup: dataResourceGroup
    containerRegistry: containerRegistry
    netApIp: netAp.outputs.privateIp
  }
}

module netAp 'modules/ap.bicep' = {
  name: '${prefix}-netap-deploy'
  params: {
    location: location
    prefix: prefix
    vmSubnet: network.outputs.vmSubnet
    vmIp: network.outputs.vmIp
    testersSubnet: network.outputs.testersSubnetRange
  }
}

module dnsNetAp 'modules/dns-add.bicep' = {
  name: '${prefix}-dns-update-netap'
  scope: resourceGroup(dnsResourceGroup)
  params: {
    ipAddress: netAp.outputs.publicIp
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
output testersIp string = testers.outputs.ip
