# fetch_publishing_profile.ps1

param (
    [string]$appName,
    [string]$resourceGroup
)

$result = az functionapp deployment list-publishing-profiles --name $appName --resource-group $resourceGroup --xml

# Output the result in JSON format
$output = @{ publishing_profile = $result } | ConvertTo-Json -Compress
Write-Output $output
