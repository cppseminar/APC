param location string
param prefix string

resource vnetTesters 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: '${prefix}-network-testers'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.1.128.0/20'
      ]
    }
  }
}



// PEERINGS
resource vnetPeeringAksTesters 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2021-05-01' = {
  name: '${prefix}-network-peer-aks-testers'
  parent: vnetAks
  properties: {
    peeringState: 'Connected'
    allowVirtualNetworkAccess: true
    peeringSyncLevel: 'FullyInSync'
    remoteVirtualNetwork: {
      id: vnetTesters.id
    }
  }
}
resource vnetPeeringTestersAks 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2021-05-01' = {
  name: '${prefix}-network-peer-testers-aks'
  parent: vnetTesters
  properties: {
    peeringState: 'Connected'
    allowVirtualNetworkAccess: true
    peeringSyncLevel: 'FullyInSync'
    remoteVirtualNetwork: {
      id: vnetAks.id
    }
  }
}
