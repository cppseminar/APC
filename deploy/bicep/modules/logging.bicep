param location string
param prefix string
param admin string = 'azureuser'


var secuirtyRules = [
  {
    name: 'Allow https'
    properties: {
      access: 'Allow'
      direction: 'Inbound'
      protocol: 'Tcp'
      priority: 1000
      description: 'Allow HTTPS traffic to cockpit server'

      sourcePortRange: '*'
      sourceAddressPrefix: '0.0.0.0'

      destinationPortRange: '443'
      destinationAddressPrefix: '0.0.0.0'
    }
  }
]

var extendedSecurityRules = [
  {
    name: '${prefix} Allow ssh'
    properties: {
      access: 'Allow'
      direction: 'Inbound'
      protocol: 'Tcp'
      priority: 1100
      description: 'Allow SSH to logging VM'

      sourcePortRange: '*'
      sourceAddressPrefix: '0.0.0.0'

      destinationPortRange: '22'
      destinationAddressPrefix: '0.0.0.0'
    }
  }
]



resource vmLoggingInterfaceSecurityGroup 'Microsoft.Network/networkSecurityGroups@2021-05-01' = {
  name: '${prefix}-vm-logging-interface-security-group'
  location: location
  properties: {
    // TODO: Use extended security rules only for setup, not all the time
    securityRules: concat(secuirtyRules, extendedSecurityRules)
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

resource vmLoggingInterface 'Microsoft.Network/networkInterfaces@2021-05-01' = {
  name: '${prefix}-vm-logging-interface'
  location: location
  properties: {
    enableAcceleratedNetworking: false
    networkSecurityGroup: {
      id: vmLoggingInterfaceSecurityGroup.id
    }
    ipConfigurations: [
      {
        name: 'ipconfig'
        properties: {
          primary: true
          privateIPAddress: '10.1.192.10'
          privateIPAllocationMethod: 'Static'
          privateIPAddressVersion: 'IPv4'
          subnet: {
            id: vnetLogging.properties.subnets[0].id
          }
          publicIPAddress: {
            id: vmLoggingIp.id
          }
        }
      }
    ]
  }
}

resource vmLoggingIp 'Microsoft.Network/publicIPAddresses@2021-05-01' = {
  name: '${prefix}-vm-logging-ip'
  location: location
  sku: {
    name: 'Standard'
    tier:'Regional'
  }
  properties: {
    publicIPAddressVersion: 'IPv4'
    publicIPAllocationMethod: 'Static'
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
      adminUsername: admin
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
              keyData: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDl/cxiJ3wJgn+ARXcJrCQ1QOQpV79yA3wBxvnkHmgxJEReOVw2PEnhX3taxVcjfYxZCDTJ9vSMWKFRxsJVff2MN259WJJCND40eTkGWS6v7/GOe80OWFSb5b8VQPtwbCzCj5czgoxtkEPzDu974zFYHM2tjVV3GrhOfGJqhsMFloe+oedk9urbjfmWZla5SeAG2h16CYY/Q1Ry3TtQR1FWZNME0opkJ9WIQzkkGnQ8Cc60eBdBRtHLswZ2pzAJ5WHoLpl3GfYVxmbJbloxIgRWteeBtADQZYXqgbuCHFNKmKEzjndOJkb4V+6xw8OR8GKdO0XXyqTRWh2mynvrQp9DtbtFeBq9kLuC6B9pDYsOj+FQTLL1HsnBgWlo6hGMB5nTYQywT6jFF3Or0LFXzfgwmyowORW7dlSksFU1yNWD8jO0QUSA8cNiXwM4P1qRcr7ySSAm1vxHrk+6H9kbDgkD0ZHwnEl1qLISDB7o3GyzcqqW+78gOZkNce3K/kuT7Ik= user@localhost'
              path: '/home/azureuser/.ssh/authorized_keys'
            }
          ]
        }
      }
    }
  }
}

output loggingIp string = vmLoggingIp.properties.ipAddress
