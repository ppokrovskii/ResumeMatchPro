# Infrastructure Management

This infrastructure is split into two resource pools:
1. Main Azure Resources (in `infra/runtime`) - managed in the neoteq.dev tenant
2. Azure AD B2C Resources (in `infra/b2c`) - managed in the ResumeMatchPro-dev tenant

## Prerequisites

- Azure CLI installed
- Terraform installed
- Access to both Azure tenants:
  - neoteq.dev (Directory ID: 9fe31206-ac65-4e49-966c-0c07561ca0f9)
  - ResumeMatchPro-dev (Directory ID: 4bab4312-676c-42cb-ac9f-4931f0438d6e)

## Managing Main Azure Resources

Use the `login-azure.ps1` script to authenticate and run Terraform commands:

```powershell
# Login and set subscription
./login-azure.ps1

# Run Terraform commands
terraform init
terraform plan -var-file="terraform.tfvars.dev"
terraform apply -var-file="terraform.tfvars.dev"
```

## Managing B2C Resources

Use the `login-b2c.ps1` script to authenticate and run Terraform commands:

```powershell
# Change to B2C directory and login
cd ../b2c
./login-b2c.ps1

# Run Terraform commands
terraform init
terraform plan -var-file="terraform.tfvars.dev"
terraform apply -var-file="terraform.tfvars.dev"
```

## Important Notes

- Always ensure you're logged into the correct tenant before running Terraform commands
- The main Azure resources are deployed to the UAE North region
- B2C resources are managed separately to maintain clear separation of concerns
- Use the provided scripts to switch between tenants when needed
