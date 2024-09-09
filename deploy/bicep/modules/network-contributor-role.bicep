param vnetName string
param subnetName string
param principalId string

// Reference the existing virtual network
resource vnet 'Microsoft.Network/virtualNetworks@2024-01-01' existing = {
  name: vnetName
}

// Reference the existing subnet within the virtual network
resource subnet 'Microsoft.Network/virtualNetworks/subnets@2024-01-01' existing = {
  name: subnetName
  parent: vnet
}

// Assign Network contributor role
resource networkContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subnet.id, principalId, 'network-contributor-role-assignment')
  scope: subnet
  properties: {
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4d97b98b-1d4f-4787-a291-c67834d212e7')  // Network contributor role id
  }
}
