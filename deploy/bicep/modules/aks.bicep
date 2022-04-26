param prefix string
param location string
param aksSubnet string

resource apcAks 'Microsoft.ContainerService/managedClusters@2022-01-01' = {
  name: '${prefix}-aks'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    kubernetesVersion: '1.23.5'
    dnsPrefix: '${prefix}-aks-dns-prefix'
    agentPoolProfiles: [
      {
        name: '${prefix}akspool'
        count: 3
        vmSize: 'Standard_B2s'
        osDiskSizeGB: 32
        osDiskType: 'Managed'
        type: 'VirtualMachineScaleSets'
        enableAutoScaling: false
        mode: 'System'
        osSKU: 'Ubuntu'
        osType: 'Linux'
        vnetSubnetID: aksSubnet
      }
    ]

    enableRBAC: false
    networkProfile: {
      networkPlugin: 'kubenet'
      networkPolicy: 'calico'
      loadBalancerProfile: {
        managedOutboundIPs: {
          count: 1
        }
      }
      loadBalancerSku:'standard' // Basic throws error for some reason
      outboundType: 'loadBalancer'
    }
  }
}
