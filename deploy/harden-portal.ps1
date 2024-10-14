

# go through all managed disks and disable public network access
$disks = az disk list | ConvertFrom-Json 
foreach ($disk in $disks) {
    Write-Output "Disabling public network access for disk: $($disk.name)"
    az disk update --ids $disk.id --public-network-access Disabled > $null
}