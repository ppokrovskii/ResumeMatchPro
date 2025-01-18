# Login to Azure with the neoteq.dev tenant
Write-Host "Logging in to Azure (neoteq.dev tenant)..."
az login --tenant "9fe31206-ac65-4e49-966c-0c07561ca0f9"

# Set the subscription to ResumeMatchPro
Write-Host "Setting subscription to ResumeMatchPro..."
az account set --subscription "114ed366-54e5-4cc8-a9cf-4f6a5fd2335c"

Write-Host "Ready to manage main Azure resources." 