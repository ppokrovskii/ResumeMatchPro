# Infrastructure Setup Guide

## Prerequisites
- Terraform version: terraform v1.8.2
- Azure CLI installed and configured
- Azure AD B2C tenant created

## Initial Setup

1. Navigate to the runtime directory:
```bash
cd .\infra\runtime\
```

2. Initialize Terraform:
```bash
terraform init
```

3. Login to Azure:
```bash
az login --scope https://graph.microsoft.com/.default
```

## Environment Configuration

### Setting up tfvars files

1. Create environment-specific tfvars files:
   - Copy `terraform.tfvars.example` to create workspace-specific files:
     ```bash
     cp terraform.tfvars.example dev.tfvars
     cp terraform.tfvars.example prod.tfvars
     ```
   - Update the values in each file according to your environment needs

### Azure AD B2C Setup

1. Create an App Registration in Azure AD B2C:
   - Navigate to Azure AD B2C > App registrations
   - Click "New registration"
   - Name: "ResumeMatchPro API"
   - Supported account types: "Accounts in any identity provider..."
   - Platform configuration: Add Web platform with redirect URI: `https://{your-function-app-name}.azurewebsites.net/.auth/login/aad/callback`

2. Configure API permissions:
   - Add Microsoft Graph permissions:
     - User.Read (delegated)
     - openid
     - profile

3. Create a client secret:
   - Go to Certificates & secrets
   - Create a new client secret
   - Copy the secret value immediately (you won't see it again)
   - Add it to your tfvars file as `BACKEND_B2C_CLIENT_SECRET`

4. Configure App ID URI:
   - Go to Expose an API
   - Set App ID URI to: `api://{client_id}`

### Working with Workspaces

1. List available workspaces:
```bash
terraform workspace list
```

2. Create workspaces if they don't exist:
```bash
terraform workspace new dev
terraform workspace new prod
```

3. Select the workspace you want to work with:
```bash
terraform workspace select dev    # For development environment
# OR
terraform workspace select prod   # For production environment
```

4. Apply the configuration:
```bash
terraform plan     # Review the changes
terraform apply    # Apply the changes
```

The workspace-specific tfvars file will be automatically loaded based on your current workspace (dev.tfvars for dev workspace, prod.tfvars for prod workspace).

## Important Notes

1. Never commit sensitive values to version control
2. Keep your API keys and secrets secure
3. Use different B2C tenants for dev and prod environments
4. Always review the plan before applying changes
5. Make sure to test changes in dev before applying to prod
6. Store B2C client secrets securely and rotate them periodically
7. Configure proper CORS settings in your B2C tenant to match your frontend URLs
