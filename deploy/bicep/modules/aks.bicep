param prefix string
param location string
param aksSubnet string
param userId string

resource apcAks 'Microsoft.ContainerService/managedClusters@2022-01-01' = {
  name: '${prefix}-aks'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userId}' : {}
    }
  }
  properties: {
    kubernetesVersion: '1.27.3'
    dnsPrefix: '${prefix}-aks-dns-prefix'
    agentPoolProfiles: [
      {
        name: '${prefix}akspool'
        count: 4
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
      loadBalancerSku: 'standard' // Basic throws error for some reason
      outboundType: 'loadBalancer'
    }
  }
}
