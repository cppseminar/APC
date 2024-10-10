param prefix string
param location string
param lbSubnet string
param lbIp string
param ssSubnet string
param dataResourceGroup string
param containerRegistry string

param admin string = 'azureuser'


resource loadBalancer 'Microsoft.Network/loadBalancers@2021-05-01' = {
  name: '${prefix}-scaleset-load-balancer'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Regional'
  }
  properties: {
    frontendIPConfigurations: [
      {
        name: '${prefix}-scaleset-lb-ip'
        properties: {
          subnet: {
            id: lbSubnet
          }
          privateIPAddress: lbIp
          privateIPAddressVersion: 'IPv4'
          privateIPAllocationMethod: 'Static'
        }
      }
    ]
    backendAddressPools: [
      {
        name: '${prefix}-lb-backend-pool'
      }
    ]
    loadBalancingRules: [
      {
        name: '${prefix}-lb-rule1'
        properties: {
          frontendPort: 80
          backendPort: 10009
          probe: {
            id: resourceId( 'Microsoft.Network/loadBalancers/probes', '${prefix}-scaleset-load-balancer', '${prefix}-lb-probe')
          }
          protocol: 'Tcp'
          backendAddressPool: {
            id: resourceId( 'Microsoft.Network/loadBalancers/backendAddressPools', '${prefix}-scaleset-load-balancer', '${prefix}-lb-backend-pool')
          }
          frontendIPConfiguration: {
            id: resourceId( 'Microsoft.Network/loadBalancers/frontendIPConfigurations', '${prefix}-scaleset-load-balancer', '${prefix}-scaleset-lb-ip')
          }
        }
      }
    ]
    probes: [
      {
        name: '${prefix}-lb-probe'
        properties: {
          protocol: 'Tcp'
          port: 10009
          intervalInSeconds: 10
          numberOfProbes: 2
        }
      }
    ]
  }
}

resource scaleSet 'Microsoft.Compute/virtualMachineScaleSets@2021-11-01' = {
  name: '${prefix}-scaleset'
  location: location
  sku: {
    capacity: 1
    name: 'Standard_F2s_v2'
    tier: 'Standard'
  }
  properties: {
    orchestrationMode: 'Uniform'
    overprovision: false
    platformFaultDomainCount: 2
    singlePlacementGroup: true
    upgradePolicy: {
      automaticOSUpgradePolicy: {
         disableAutomaticRollback: false
         enableAutomaticOSUpgrade: false
      }
      mode: 'Automatic'
    }
    virtualMachineProfile: {
      diagnosticsProfile: {
        bootDiagnostics: {
          enabled: false
        }
      }
      osProfile: {
         adminUsername: admin
         computerNamePrefix: '${prefix}-ssvm-'
         linuxConfiguration: {
           provisionVMAgent: true
           patchSettings: {
            patchMode: 'ImageDefault'
           }
           ssh: {
             publicKeys: [
               {
                 path: '/home/${admin}/.ssh/authorized_keys'
                 keyData: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDl/cxiJ3wJgn+ARXcJrCQ1QOQpV79yA3wBxvnkHmgxJEReOVw2PEnhX3taxVcjfYxZCDTJ9vSMWKFRxsJVff2MN259WJJCND40eTkGWS6v7/GOe80OWFSb5b8VQPtwbCzCj5czgoxtkEPzDu974zFYHM2tjVV3GrhOfGJqhsMFloe+oedk9urbjfmWZla5SeAG2h16CYY/Q1Ry3TtQR1FWZNME0opkJ9WIQzkkGnQ8Cc60eBdBRtHLswZ2pzAJ5WHoLpl3GfYVxmbJbloxIgRWteeBtADQZYXqgbuCHFNKmKEzjndOJkb4V+6xw8OR8GKdO0XXyqTRWh2mynvrQp9DtbtFeBq9kLuC6B9pDYsOj+FQTLL1HsnBgWlo6hGMB5nTYQywT6jFF3Or0LFXzfgwmyowORW7dlSksFU1yNWD8jO0QUSA8cNiXwM4P1qRcr7ySSAm1vxHrk+6H9kbDgkD0ZHwnEl1qLISDB7o3GyzcqqW+78gOZkNce3K/kuT7Ik= user@localhost'
               }
             ]
           }
         } // linuxConfig
         customData: base64(format(loadTextContent('cloud-init.yaml'), containerRegistry))
      } // osprofile
      networkProfile: {
        // healthProbe:
        networkInterfaceConfigurations: [
          {
            name: '${prefix}-netifconfig'
            properties: {
              primary: true
              ipConfigurations: [
                {
                  name: '${prefix}-netifipconfig'
                  properties: {
                    loadBalancerBackendAddressPools: [
                      {
                        id: loadBalancer.properties.backendAddressPools[0].id
                      }
                    ]
                    privateIPAddressVersion: 'IPv4'
                    subnet: {
                      id: ssSubnet
                    }
                  }
                }
              ]
            }
          }
        ] // network IF configs
      } // network profile
      storageProfile: {
        osDisk: {
          createOption: 'FromImage'
          diskSizeGB: 32
          managedDisk: {
            storageAccountType: 'Standard_LRS'
          }
        }
        imageReference: {
          publisher: 'canonical'
          offer: '0001-com-ubuntu-server-jammy'
          sku: '22_04-lts'
          version: 'latest'
        }
      }
    }
  }

  identity: {
    type: 'SystemAssigned'
  }
}

module scaleSetRole 'roles/acr-pull-role.bicep' = {
  name: '${prefix}-scaleset-role'
  scope: resourceGroup(dataResourceGroup)
  params: {
    registryName: containerRegistry
    principalId: scaleSet.identity.principalId
  }
}

output ip string = loadBalancer.properties.frontendIPConfigurations[0].properties.privateIPAddress
