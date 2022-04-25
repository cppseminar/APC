
param location string = 'germanywestcentral'

@minLength(1)
@maxLength(5)
param prefix string


module apcCompute 'modules/aks.bicep' = {
  name: '${prefix}-apc-deploy'
  params: {
    location: location
    prefix: prefix
    aksSubnet: network.outputs.aksSubnet
  }
}

module network 'modules/mainnet.bicep' = {
  name: '${prefix}-vnet-deploy'
  params: {
    location: location
    prefix: prefix
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
