# https://andrewilson.co.uk/post/2024/07/removing-orphaned-rbac-role-assignments/
# the problem is that the role assignment is not deleted when the service principal is deleted
# and since in bicep we create a new system assigned identity every time we deploy, we end up 
# with a lot of orphaned role assignments when redeploying the same deployment

param (
    [string]$ResourceGroupName
)

Write-Output "Fetching all role assignments..."
$roleAssignments = az role assignment list --all | ConvertFrom-Json

Write-Output "Filtering orphaned role assignments in resource group: $ResourceGroupName..."
$orphaned = $roleAssignments | Where-Object { ($_.principalName -eq "") -and ($_.scope -match "resourcegroups/$ResourceGroupName") }

Write-Output "Found $($orphaned.Count) orphaned role assignments."
if ($orphaned.Count -gt 0) {
    Write-Output "Deleting orphaned role assignments..."
    $orphaned | ForEach-Object { 
        Write-Output "Deleting role assignment with ID: $($_.id)"
        az role assignment delete --ids $_.id 
    }
} else {
    Write-Output "No orphaned role assignments found."
}