param ipAddress string
param subDomain string
param resourceName string


resource apcDnsZone 'Microsoft.Network/dnsZones@2018-05-01' existing = {
  name: resourceName
}

resource dnsEntry 'Microsoft.Network/dnsZones/A@2018-05-01' = {
  name: subDomain
  parent: apcDnsZone
  properties:{
    TTL: 300
    ARecords:[
      {
        ipv4Address: ipAddress
      }
    ]
  }
}
