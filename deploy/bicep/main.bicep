
param location string = 'germanywestcentral'

@minLength(1)
@maxLength(5)
param prefix string



module nets 'modules/networks.bicep' = {
  name: 'asfd'
  params: {
    location: location
    prefix: prefix
  }
}

module logging 'modules/logging.bicep' = {
  name: 'logging'
  params: {

  }
}
