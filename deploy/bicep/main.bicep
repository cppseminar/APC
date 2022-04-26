
param location string = 'germanywestcentral'

@minLength(1)
@maxLength(5)
param prefix string

@secure()
param dbPassword string


module network 'modules/mainnet.bicep' = {
  name: '${prefix}-vnet-deploy'
  params: {
    location: location
    prefix: prefix
  }
}

module apcPostgres 'modules/postgres.bicep' = {
  name: '${prefix}-postgres-deploy'
  params: {
    vnetId: network.outputs.vnetId
    location: location
    prefix: prefix
    subnet: network.outputs.dbSubnet
    password: dbPassword
  }
}

module apcCompute 'modules/aks.bicep' = {
  name: '${prefix}-apc-deploy'
  params: {
    location: location
    prefix: prefix
    aksSubnet: network.outputs.aksSubnet
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
