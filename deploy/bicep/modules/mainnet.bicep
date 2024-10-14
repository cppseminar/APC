param location string
param prefix string
param tags object = {}

var vmIp = '10.12.64.5'
var testersLoadBalancerIp = '10.12.0.25'

var testersSubnetRange = '10.13.0.0/16'
var aksSubnetRange = '10.14.0.0/16'

resource apSubnetNsg 'Microsoft.Network/networkSecurityGroups@2024-01-01' = {
  name: '${prefix}-vnet-ap-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'allow-ssh'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '22'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 100
          direction: 'Inbound'
        }
      },{
        name: 'allow-journal-remote'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '19532'
          sourceAddressPrefix: 'VirtualNetwork'
          destinationAddressPrefix: 'VirtualNetwork'
          access: 'Allow'
          priority: 101
          direction: 'Inbound'
        }
      },{
        name: 'deny-all'
        properties: {
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Deny'
          priority: 1000
          direction: 'Inbound'
        }
      }
    ]
  }
}

resource testersSubnetNsg 'Microsoft.Network/networkSecurityGroups@2024-01-01' = {
  name: '${prefix}-vnet-testers-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'allow-ssh'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '22'
          sourceAddressPrefix: vmIp
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 100
          direction: 'Inbound'
        }
      },{
        name: 'allow-queued'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '10009'
          sourceAddressPrefix: 'VirtualNetwork'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 101
          direction: 'Inbound'
        }
      },{
        name: 'deny-all'
        properties: {
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Deny'
          priority: 1000
          direction: 'Inbound'
        }
      }
    ]
  }
}

resource lbTestersSubnetNsg 'Microsoft.Network/networkSecurityGroups@2024-01-01' = {
  name: '${prefix}-vnet-lb-testers-nsg'
  location: location
  properties: {
    securityRules: [
      {
        // why this works, i have no idea
        name: 'deny-all'
        properties: {
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Deny'
          priority: 1000
          direction: 'Inbound'
        }
      }
    ]
  }
}

resource aksSubnetNsg 'Microsoft.Network/networkSecurityGroups@2024-01-01' = {
  name: '${prefix}-vnet-aks-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'allow-ingress-http'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '80'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 103
          direction: 'Inbound'
        }
      },{
        name: 'allow-ingress-https'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 104
          direction: 'Inbound'
        }
      }
    ]
  }
}

resource apcVnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: '${prefix}-vnet'
  location: location
  tags: tags
  properties: {
    enableDdosProtection: false
    flowTimeoutInMinutes: 10
    encryption: {
      enabled: true
      enforcement: 'AllowUnencrypted'
    }
    addressSpace: {
      addressPrefixes: [
        '10.12.0.0/14'
      ]
    }
    subnets: [
      {
        name: 'aks-subnet'
        properties:{
          addressPrefix: aksSubnetRange
          privateEndpointNetworkPolicies: 'NetworkSecurityGroupEnabled'
          networkSecurityGroup: {
            id: aksSubnetNsg.id
          }
        }
      }
      {
        name: 'testers-subnet'
        properties: {
          addressPrefix: testersSubnetRange
          privateEndpointNetworkPolicies: 'NetworkSecurityGroupEnabled'
          networkSecurityGroup: {
            id: testersSubnetNsg.id
          }
        }
      }
      {
        name: 'lb-subnet'
        properties: {
          addressPrefix: '10.12.0.0/18'
          privateEndpointNetworkPolicies: 'NetworkSecurityGroupEnabled'
          networkSecurityGroup: {
            id: lbTestersSubnetNsg.id
          }
        }
      }
      {
        name: 'vm-subnet'
        properties: {
          addressPrefix: '10.12.64.0/18'
          privateEndpointNetworkPolicies: 'NetworkSecurityGroupEnabled'
          networkSecurityGroup: {
            id: apSubnetNsg.id
          }
        }
      }
    ]
  }
}

output lbIp string = testersLoadBalancerIp
output vmIp string = vmIp
output vnetName string = apcVnet.name
output aksSubnetName string = apcVnet.properties.subnets[0].name
output testersSubnet string = apcVnet.properties.subnets[1].id
output testersSubnetRange string = apcVnet.properties.subnets[1].properties.addressPrefix
output lbSubnet string = apcVnet.properties.subnets[2].id
output vmSubnet string = apcVnet.properties.subnets[3].id
