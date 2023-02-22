param location string
param prefix string
param vmSubnet string
param vmIp string
param admin string = 'azureuser'




resource vmNetApInterfaceSecurityGroup 'Microsoft.Network/networkSecurityGroups@2021-05-01' = {
  name: '${prefix}-vm-netap-interface-security-group'
  location: location
  properties: {
    securityRules: [
      {
        name: 'allow-ssh'
        properties: {
          access: 'Allow'
          protocol: 'Tcp'
          direction: 'Inbound'
          destinationPortRange: '22'
          destinationAddressPrefix: '0.0.0.0/0'
          sourceAddressPrefix: '0.0.0.0/0'
          sourcePortRange: '*'
          priority: 1000
        }
      }
    ]
  }
}

resource vmNetApIp 'Microsoft.Network/publicIPAddresses@2021-05-01' = {
  name: '${prefix}-vm-netap-ip'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Regional'
  }
  properties: {
    publicIPAddressVersion: 'IPv4'
    publicIPAllocationMethod: 'Static'
  }
}


resource vmNetApInterface 'Microsoft.Network/networkInterfaces@2021-05-01' = {
  name: '${prefix}-vm-netap-interface'
  location: location
  properties: {
    enableAcceleratedNetworking: false
    networkSecurityGroup: {
      id: vmNetApInterfaceSecurityGroup.id
    }
    ipConfigurations: [
      {
        name: 'ipconfig'
        properties: {
          primary: true
          privateIPAddressVersion: 'IPv4'
          privateIPAllocationMethod: 'Static'
          privateIPAddress: vmIp
          subnet: {
            id: vmSubnet
          }
          publicIPAddress: {
            id: vmNetApIp.id
          }
        }
      }
    ]
  }
}


resource vmNetAp 'Microsoft.Compute/virtualMachines@2021-11-01' = {
  name: '${prefix}-vm-netap'
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
        name: '${prefix}-vm-netap-disk-os'
        managedDisk: {
          storageAccountType: 'Standard_LRS'
        }
      }
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: vmNetApInterface.id
        }
      ]
    }
    osProfile: {
      computerName: '${prefix}netap'
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

output netApIp string = vmNetApIp.properties.ipAddress
