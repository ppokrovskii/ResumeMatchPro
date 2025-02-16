# Login to Azure with the dev tenant (NETORGFT14683197.onmicrosoft.com)
Write-Host "Logging in to Azure (dev tenant)..."
$loginResult = az login --tenant "NETORGFT14683197.onmicrosoft.com"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to login to Azure. Please check your credentials and try again."
    exit 1
}

# Verify we're in the correct tenant
$tenantId = az account show --query "tenantId" -o tsv
if ($tenantId -ne "9fe31206-ac65-4e49-966c-0c07561ca0f9") {
    Write-Error "Wrong tenant ID. Expected: 9fe31206-ac65-4e49-966c-0c07561ca0f9, Got: $tenantId"
    exit 1
}

# Set the subscription to ResumeMatchPro dev subscription
Write-Host "Setting subscription to ResumeMatchPro dev subscription..."
$subResult = az account set --subscription "b9687d4b-5767-4f6e-bbc5-6afc09b3117f"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to set subscription. Please check if you have access to the ResumeMatchPro dev subscription."
    exit 1
}

# Verify the current context
Write-Host "Verifying current context..."
$context = az account show --query "{Subscription:name, SubscriptionId:id, Tenant:tenantId, User:user.name}" -o table
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to verify current context."
    exit 1
}

Write-Host "Successfully logged in and set context:"
Write-Host $context
Write-Host "Ready to manage Azure resources." 