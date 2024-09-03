param prefix string
param location string
param aksSubnet string
param registryName string

resource apcAks 'Microsoft.ContainerService/managedClusters@2024-02-01' = {
  name: '${prefix}-aks'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    kubernetesVersion: '1.28.12'
    dnsPrefix: '${prefix}-aks-dns-prefix'
    agentPoolProfiles: [
      {
        name: '${prefix}akspool'
        count: 4
        vmSize: 'Standard_B2als_v2'
        osDiskSizeGB: 32
        osDiskType: 'Managed'
        type: 'VirtualMachineScaleSets'
        enableAutoScaling: true
        minCount: 3
        maxCount: 6
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

module aksKubeletRole 'aks-role.bicep' = {
  name: '${prefix}-aks-kubelet-role'
  scope: resourceGroup('${prefix}-data')
  params: {
    registryName: registryName
    kubeletPrincipalId: apcAks.properties.identityProfile.kubeletidentity.objectId
  }
}
