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

resource vnetAks 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: '${prefix}-network-aks'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.1.0.0/20'
      ]
    }
  }
}

resource vnetLogging 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: '${prefix}-network-logging'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.1.192.0/20'
      ]
    }
    subnets: [
      {
        name: 'subnet1'
        properties: {
          addressPrefix: '10.1.192.0/20'
        }
      }
    ]
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


resource vnetPeeringLoggingTesters 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2021-05-01' = {
  name: '${prefix}-network-peer-logging-testers'
  parent: vnetLogging
  properties: {
    peeringState: 'Connected'
    allowVirtualNetworkAccess: true
    peeringSyncLevel: 'FullyInSync'
    remoteVirtualNetwork: {
      id: vnetTesters.id
    }
  }
}

resource vnetPeeringTestersLogging 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2021-05-01' = {
  name: '${prefix}-network-peer-testers-logging'
  parent: vnetTesters
  properties: {
    peeringState: 'Connected'
    allowVirtualNetworkAccess: true
    peeringSyncLevel: 'FullyInSync'
    remoteVirtualNetwork: {
      id: vnetLogging.id
    }
  }
}




// Logging



resource vmLoggingInterface 'Microsoft.Network/networkInterfaces@2021-05-01' = {
  name: '${prefix}-vm-logging-interface'
  location: location
  properties: {
    enableAcceleratedNetworking: false
    ipConfigurations: [
      {
        name: 'ipconfig'
        properties: {
          primary: true
          privateIPAddress: '10.1.192.5'
          privateIPAddressVersion: 'IPv4'
          subnet: {
            id: vnetLogging.properties.subnets[0].id
          }
        }
      }
    ]
  }
}


resource vmLogging 'Microsoft.Compute/virtualMachines@2021-11-01' = {
  name: '${prefix}-vm-logging'
  location: location

  properties: {
    diagnosticsProfile: {
      bootDiagnostics: {
        enabled: false
      }
    }
    hardwareProfile: {
      vmSize: 'Standard_B1s'
    }
    storageProfile: {
      imageReference: {
        publisher: 'canonical'
        offer: '0001-com-ubuntu-server-focal'
        sku: '20_04-lts'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        osType: 'Linux'
        name: '${prefix}-vm-logging-disk-os'
        managedDisk: {
          storageAccountType: 'Standard_LRS'
        }
      }
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: vmLoggingInterface.id
        }
      ]
    }
    osProfile: {
      computerName: '${prefix}Logger'
      adminUsername: 'azureuser'
      allowExtensionOperations: true
      linuxConfiguration: {
        disablePasswordAuthentication: true
        provisionVMAgent: true
        patchSettings: {
          assessmentMode: 'ImageDefault'
          patchMode: 'ImageDefault'
        }
        ssh: {
          publicKeys: [
            {
              keyData: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC/J0Sh5iS1fDZ5z1V+OvF/OD0P\r\nnPKb2fWLZiB0roC9Rioo4rPi9F09mSBvp5F0LTy+rSgO4LzgS3Wxulxfo8xuiywz\r\nAtMI2f2XCYHTjIOAzeuZ7pTKTM4pwrPda6ym322OMwu9CwBdjbmvOsn/jJ0Lt1rD\r\nuxSZq0zE8t/QjlOZF4x+3Iw+zfxjSIuqNVyYsd+0Sj6N5kGYBnaTAlBO7aTjfCTo\r\naguKQQjSY0tjYc4CnccLSqchPR4bEMopSl4ICYjlprKo7Lk5FEoHdm4zS52PscTM\r\njPsazkObN6g63/1C1OWky1mtIcjI/VzAwmLm1+pAZMiSvTER3yiOTnLPeoxgFMcW\r\n26jxNz5bTB97Nb+j0FjiYTWKsrv753jHWIsqO6DiHzBy4PmO9h8RIDe4dVMHWNd+\r\nqKqRXPR9BMV9tSe2+UzrCnbcQm+Lzj07EAu6TKeTyio8Q/vetkKfObTTtcslz0Dw\r\nyejzTxhZDVbN3Fj0JwMD55WAKXJQy9oznDjsyjE= generated-by-azure\r\n'
              path: '/home/azureuser/.ssh/authorized_keys'
            }
          ]
        }
      }
    }
  }
}
