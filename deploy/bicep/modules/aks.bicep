param prefix string
param location string
param vnetName string
param subnetName string
param registryName string

// Reference the existing virtual network
resource vnet 'Microsoft.Network/virtualNetworks@2024-01-01' existing = {
  name: vnetName
}

// Reference the existing subnet within the virtual network
resource aksSubnet 'Microsoft.Network/virtualNetworks/subnets@2024-01-01' existing = {
  name: subnetName
  parent: vnet
}

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
        vnetSubnetID: aksSubnet.id
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

module aksKubeletRole 'acr-pull-role.bicep' = {
  name: '${prefix}-aks-kubelet-role'
  scope: resourceGroup('${prefix}-data')
  params: {
    registryName: registryName
    principalId: apcAks.properties.identityProfile.kubeletidentity.objectId
  }
}

module aksRole 'network-contributor-role.bicep' = {
  name: '${prefix}-aks-role'
  params: {
    vnetName: vnet.name
    subnetName: aksSubnet.name
    principalId: apcAks.identity.principalId
  }
}
