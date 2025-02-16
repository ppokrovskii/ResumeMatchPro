param(
    [Parameter(Mandatory = $true)]
    [string]$UserId,

    [Parameter(Mandatory = $true)]
    [ValidateSet('dev', 'prod')]
    [string]$Environment
)

# Load environment variables based on environment
$envFile = "../azfunctions/.env.$Environment"
if (-not (Test-Path $envFile)) {
    Write-Error "Environment file not found: $envFile"
    exit 1
}

# Read environment variables
$envContent = Get-Content $envFile
foreach ($line in $envContent) {
    if ($line -match '^([^=]+)=(.*)$') {
        $key = $matches[1]
        $value = $matches[2]
        Set-Item -Path "env:$key" -Value $value
    }
}

# Get B2C tenant details from environment variables
$tenantId = $env:AZURE_AD_B2C_TENANT_ID
$clientId = $env:AZURE_AD_B2C_CLIENT_ID
$clientSecret = $env:AZURE_AD_B2C_CLIENT_SECRET
$b2cDomain = $env:AZURE_AD_B2C_DOMAIN

# Get access token for Microsoft Graph API
$tokenUrl = "https://login.microsoftonline.com/$tenantId/oauth2/v2.0/token"
$scope = "https://graph.microsoft.com/.default"

$tokenBody = @{
    grant_type    = "client_credentials"
    client_id     = $clientId
    client_secret = $clientSecret
    scope         = $scope
}

try {
    $tokenResponse = Invoke-RestMethod -Uri $tokenUrl -Method Post -Body $tokenBody
    $accessToken = $tokenResponse.access_token
}
catch {
    Write-Error "Failed to get access token: $_"
    exit 1
}

# Get user details
$graphApiUrl = "https://graph.microsoft.com/v1.0/users/$UserId"
$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type"  = "application/json"
}

try {
    $user = Invoke-RestMethod -Uri $graphApiUrl -Headers $headers -Method Get
    Write-Host "Current user details:"
    Write-Host ($user | ConvertTo-Json)
}
catch {
    Write-Error "Failed to get user details: $_"
    exit 1
}

# Confirm action
$confirmation = Read-Host "Do you want to make this user an admin? (y/n)"
if ($confirmation -ne 'y') {
    Write-Host "Operation cancelled"
    exit 0
}

# Update user extension attribute
$extensionName = "extension_$($clientId.Replace('-', ''))_isAdmin"
$updateBody = @{
    "$extensionName" = $true
} | ConvertTo-Json

try {
    $updatedUser = Invoke-RestMethod -Uri $graphApiUrl -Headers $headers -Method Patch -Body $updateBody
    Write-Host "User updated successfully. Please sign out and sign in again for changes to take effect."
}
catch {
    Write-Error "Failed to update user: $_"
    exit 1
} 