param prefix string
param location string
param aksSubnet string

// resource vnetAks 'Microsoft.Network/virtualNetworks@2021-02-01' = {
//   name: '${prefix}-network-aks'
//   location: location
//   properties: {
//     addressSpace: {
//       addressPrefixes: [
//         '10.14.0.0/15'
//       ]
//     }
//     enableDdosProtection: false
//     subnets: [
//       {
//         name: 'aks-subnet'
//         properties: {
//           addressPrefix: '10.14.0.0/16'
//         }
//       }
//       {
//         name: 'poolsubnet'
//         properties: {
//           addressPrefix: '10.15.0.0/16'
//         }
//       }
//     ]
//   }
// }


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
