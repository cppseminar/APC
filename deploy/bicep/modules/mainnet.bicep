param location string
param prefix string

resource apcVnet 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: '${prefix}-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.12.0.0/14'
      ]
    }
    subnets: [
      {
        name: 'aks-subnet'
        properties:{
          addressPrefix: '10.14.0.0/16'
        }
      }
      {
        name: 'sset-subnet'
        properties: {
          addressPrefix: '10.13.0.0/16'
        }
      }
      {
        name: 'lb-subnet'
        properties: {
          addressPrefix: '10.12.0.0/18'
        }
      }
      {
        name: 'vm-subnet'
        properties: {
          addressPrefix: '10.12.64.0/18'
        }
      }
      {
        name: 'dbSubnet'
        properties: {
          addressPrefix: '10.12.128.0/17'
          delegations: [
            {
              name: '${prefix}-subnet-postgres'
              properties: {
                serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
              }
            }
          ]
        }
      }
      {
        name: 'reserved2'
        properties: {
          addressPrefix: '10.15.0.0/16'
        }
      }
    ]
  }
}

output lbIp string = '10.12.0.25'
output vmIp string = '10.12.64.5'
output vnetId string = apcVnet.id
output aksSubnet string = apcVnet.properties.subnets[0].id
output ssetSubnet string = apcVnet.properties.subnets[1].id
output lbSubnet string = apcVnet.properties.subnets[2].id
output vmSubnet string = apcVnet.properties.subnets[3].id
output dbSubnet string = apcVnet.properties.subnets[4].id
