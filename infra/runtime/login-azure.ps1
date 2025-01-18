# Login to Azure with the neoteq.dev tenant (NETORGFT14683197.onmicrosoft.com)
Write-Host "Logging in to Azure (neoteq.dev tenant)..."
$loginResult = az login --tenant "NETORGFT14683197.onmicrosoft.com"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to login to Azure. Please check your credentials and try again."
    exit 1
}

# Set the subscription to ResumeMatchPro
Write-Host "Setting subscription to ResumeMatchPro..."
$subResult = az account set --subscription "ResumeMatchPro"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to set subscription. Please check if you have access to the ResumeMatchPro subscription."
    exit 1
}

# Verify the current context
Write-Host "Verifying current context..."
$context = az account show --query "{Subscription:name, Tenant:tenantId, User:user.name}" -o table
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to verify current context."
    exit 1
}

Write-Host "Successfully logged in and set context:"
Write-Host $context
Write-Host "Ready to manage Azure resources." 