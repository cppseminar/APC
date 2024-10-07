param ipName string
param principalId string

// Reference the existing ip address
resource ip 'Microsoft.Network/publicIPAddresses@2024-01-01' existing = {
  name: ipName
}

// Assign Network contributor role
resource networkContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(ip.id, principalId, 'network-contributor-role-assignment')
  scope: ip
  properties: {
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4d97b98b-1d4f-4787-a291-c67834d212e7')  // Network contributor role id
    principalType: 'ServicePrincipal'
  }
}
