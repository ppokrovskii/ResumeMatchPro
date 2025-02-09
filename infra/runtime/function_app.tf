# Create an Azure Function App
resource "azurerm_linux_function_app" "resumematchpro" {
    name                      = "${var.project_name}-${terraform.workspace}-function-app"
    location                  = azurerm_resource_group.rg.location
    resource_group_name       = azurerm_resource_group.rg.name
    service_plan_id           = azurerm_service_plan.resumematchpro.id
    storage_account_name      = azurerm_storage_account.storage.name
    storage_account_access_key = azurerm_storage_account.storage.primary_access_key

    site_config {
        application_stack {
            python_version = "3.11"
        }
        
        cors {
            allowed_origins = split(",", var.MAIN_FRONTEND_URLS)
            support_credentials = true
        }
    }

    auth_settings_v2 {
        auth_enabled = true
        require_authentication = true
        default_provider = "azureactivedirectory"
        require_https = true
        
        active_directory_v2 {
            client_id = var.BACKEND_B2C_CLIENT_ID
            tenant_auth_endpoint = "https://${var.B2C_TENANT_NAME}.b2clogin.com/${var.B2C_TENANT_NAME}.onmicrosoft.com/B2C_1_signupsignin/v2.0"
            # client_secret_setting_name = "BACKEND_B2C_CLIENT_SECRET"
            allowed_audiences = ["api://${var.BACKEND_B2C_CLIENT_ID}"]
        }

        login {
            token_store_enabled = true
        }
    }

    app_settings = {
        "FUNCTIONS_WORKER_RUNTIME" = "python"
        "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.ResumeMatchProInsights.instrumentation_key
        "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.storage.primary_connection_string
        "AzureWebJobsStorage" = azurerm_storage_account.storage.primary_connection_string
        
        "AZURE_OPENAI_API_KEY" = var.AZURE_OPENAI_API_KEY
        "AZURE_OPENAI_ENDPOINT" = var.AZURE_OPENAI_ENDPOINT
        "AZURE_OPENAI_DEPLOYMENT_NAME" = var.AZURE_OPENAI_DEPLOYMENT_NAME

        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" = var.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
        "AZURE_DOCUMENT_INTELLIGENCE_KEY" = var.AZURE_DOCUMENT_INTELLIGENCE_KEY

        "COSMOS_URL" = azurerm_cosmosdb_account.cosmosdb.endpoint
        "COSMOS_KEY" = azurerm_cosmosdb_account.cosmosdb.primary_key
        "COSMOS_DB_NAME" = "${var.project_name}-${terraform.workspace}"

        # CORS Configuration
        "ALLOWED_ORIGINS" = var.MAIN_FRONTEND_URLS

        # B2C Configuration
        # "BACKEND_B2C_CLIENT_SECRET" = var.BACKEND_B2C_CLIENT_SECRET
        "ALLOWED_REDIRECT_URIS" = terraform.workspace == "dev" ? "https://oauth.pstmn.io/v1/callback" : ""
    }

    lifecycle {
        ignore_changes = [
            app_settings["APPINSIGHTS_INSTRUMENTATIONKEY"],
            app_settings["AzureWebJobsStorage"]
        ]
    }
}

# Create an App Service Plan
resource "azurerm_service_plan" "resumematchpro" {
    name                = "${var.project_name}-${terraform.workspace}-service-plan"
    location            = azurerm_resource_group.rg.location
    resource_group_name = azurerm_resource_group.rg.name
    os_type             = "Linux"
    sku_name            = "Y1"
}

# Output Function App Name
output "FUNCTION_APP_NAME" {
    value = azurerm_linux_function_app.resumematchpro.name
}

# Output Function App URL
output "FUNCTION_APP_URL" {
    value = "https://${azurerm_linux_function_app.resumematchpro.default_hostname}/api"
}

# Output Function App publish profile
output "GET_AZFUNCTIONS_PUBLISHING_PROFILE" {
    value = "az functionapp deployment list-publishing-profiles --name ${azurerm_linux_function_app.resumematchpro.name} --resource-group ${azurerm_resource_group.rg.name} --xml"
    description = "Run this command in your shell to retrieve the Azure Function App's publishing profile."
}

# Output B2C Authentication URLs
output "B2C_AUTH_URL" {
    value = "https://${var.B2C_TENANT_NAME}.b2clogin.com/${var.B2C_TENANT_NAME}.onmicrosoft.com/B2C_1_signupsignin/oauth2/v2.0/authorize"
    description = "Use this URL for OAuth2 authorization in Postman"
}

output "B2C_TOKEN_URL" {
    value = "https://${var.B2C_TENANT_NAME}.b2clogin.com/${var.B2C_TENANT_NAME}.onmicrosoft.com/B2C_1_signupsignin/oauth2/v2.0/token"
    description = "Use this URL for OAuth2 token endpoint in Postman"
}

output "B2C_SCOPE" {
    value = "openid offline_access https://${var.B2C_TENANT_NAME}.onmicrosoft.com/${var.BACKEND_B2C_CLIENT_ID}/user_impersonation"
    description = "Use this scope for OAuth2 configuration in Postman"
}