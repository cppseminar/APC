
param location string = 'germanywestcentral'

@minLength(1)
@maxLength(5)
param prefix string

param containerRegistry string


module network 'modules/mainnet.bicep' = {
  name: '${prefix}-vnet-deploy'
  params: {
    location: location
    prefix: prefix
  }
}

module apcCompute 'modules/aks.bicep' = {
  name: '${prefix}-apc-deploy'
  params: {
    location: location
    prefix: prefix
    aksSubnet: network.outputs.aksSubnet
    userId: aksIdentity.id
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
    acrIdentity: acrIdentity.id
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

module dns 'modules/dnsAdd.bicep' = {
  name: 'dnsUpdate'
  scope: resourceGroup('apc-dns')
  params: {
    ipAddress: netAp.outputs.netApIp
    resourceName: 'apc.l33t.party'
    subDomain: 'netap'
  }
}

resource aksIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' existing = {
  scope: resourceGroup('apc-data')
  name: 'apc-aks-user'
}

resource acrIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' existing = {
  scope: resourceGroup('apc-data')
  name: '${containerRegistry}-user'
}
