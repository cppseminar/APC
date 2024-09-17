// Deploy logging infra

param location string = 'germanywestcentral'

@minLength(1)
@maxLength(5)
param prefix string


module logging 'modules/logging.bicep' = {
  name: 'logging'
  params: {
    location: location
    prefix: prefix
  }
}

module dns 'modules/dns-add.bicep' = {
  name: 'dnsUpdate'
  scope: resourceGroup('apc-dns')
  params: {
    ipAddress: logging.outputs.loggingIp
    resourceName: 'apc.l33t.party'
    subDomain: 'management'
  }
}
