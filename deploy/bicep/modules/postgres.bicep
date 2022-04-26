param location string
param prefix string
param subnet string
param vnetId string

@secure()
param password string

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2021-06-01' = {
  name: '${prefix}-postgres'
  location: location
  sku:{
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: 'azureuser'
    administratorLoginPassword: password
    storage:  {
      storageSizeGB: 16
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    version: '13'
    network: {
      delegatedSubnetResourceId: subnet
      privateDnsZoneArmResourceId: apcPrivateDnsZone.id
    }
  }
  dependsOn: [
    apcPrivateDnsZoneLink
  ]
}

// resource postgresPw1 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2021-06-01' = {
//    name: 'azure.accepted_password_auth_method'
//    parent: postgres
//    properties: {
//      value: 'md5'
//    }
// }

// resource postgresPw2 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2021-06-01' = {
//   name: 'password_encryption'
//    parent: postgres
//    properties: {
//     value: 'md5'
//   }
// }

resource apcPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: '${prefix}-dev.private.postgres.database.azure.com'
  location: 'global'
}

resource apcPrivateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  name: '${prefix}-dns-vnet-link'
  location: 'global'
  parent: apcPrivateDnsZone
  properties: {
    registrationEnabled: true
    virtualNetwork: {
      id: vnetId
    }
  }
}
