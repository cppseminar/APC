param registryName string
param kubeletPrincipalId string

resource acr 'Microsoft.ContainerRegistry/registries@2022-12-01' existing = {
  name: registryName
}


// Assign AcrPull role to the kubelet identity for pulling images from ACR
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, kubeletPrincipalId, 'acrpull-role-assignment')
  scope: acr
  properties: {
    principalId: kubeletPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')  // AcrPull role id
  }
}
