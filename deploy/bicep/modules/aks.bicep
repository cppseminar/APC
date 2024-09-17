param prefix string
param location string
param vnetName string
param subnetName string
param dataResourceGroup string
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

// create public ip address that serve as aks ingress ip
resource aksIngressIp 'Microsoft.Network/publicIPAddresses@2024-01-01' = {
  name: '${prefix}-aks-ingress-ip'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAddressVersion: 'IPv4'
    publicIPAllocationMethod: 'Static'
  }
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

module aksKubeletRole 'roles/acr-pull-role.bicep' = {
  name: '${prefix}-aks-kubelet-role'
  scope: resourceGroup(dataResourceGroup)
  params: {
    registryName: registryName
    principalId: apcAks.properties.identityProfile.kubeletidentity.objectId
  }
}

module aksRoleSubnet 'roles/network-contributor-role-subnet.bicep' = {
  name: '${prefix}-aks-role-subnet'
  params: {
    vnetName: vnet.name
    subnetName: aksSubnet.name
    principalId: apcAks.identity.principalId
  }
}

module aksRoleIngressIp 'roles/network-contributor-role-ip.bicep' = {
  name: '${prefix}-aks-role-ingress-ip'
  params: {
    ipName: aksIngressIp.name
    principalId: apcAks.identity.principalId
  }
}

// output of whole resources is experimental now, can be changed in future
output publicIpName string = aksIngressIp.name
output publicIp string = aksIngressIp.properties.ipAddress

output aksName string = apcAks.name

