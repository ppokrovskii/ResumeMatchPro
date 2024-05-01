variable "AZURE_OPENAI_API_KEY" {
    description = "Azure OpenAI API Key"
}

variable "AZURE_DOCUMENT_INTELLIGENCE_KEY" {
    description = "Azure Document Intelligence Key"
}

# Create an Azure Function App
resource "azurerm_function_app" "resumematchpro" {
    name                      = "${var.project_name}-${terraform.workspace}-function-app"
    location                  = azurerm_resource_group.rg.location
    resource_group_name       = azurerm_resource_group.rg.name
    app_service_plan_id       = azurerm_app_service_plan.resumematchpro.id
    storage_account_name      = azurerm_storage_account.storage.name
    storage_account_access_key = azurerm_storage_account.storage.primary_access_key
    version                   = "~4"
    
    app_settings = {
        "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.ResumeMatchProInsights.instrumentation_key
        "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.storage.primary_connection_string

        "AZURE_OPENAI_API_KEY" = var.AZURE_OPENAI_API_KEY
        "AZURE_OPENAI_ENDPOINT" = "https://neogpt.openai.azure.com/"
        "AZURE_OPENAI_DEPLOYMENT_NAME" = "gpt35turbo16k"

        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" = "https://docintpavelpweurope.cognitiveservices.azure.com/"
        "AZURE_DOCUMENT_INTELLIGENCE_KEY" = var.AZURE_DOCUMENT_INTELLIGENCE_KEY

        "COSMOS_URL" = azurerm_cosmosdb_account.cosmosdb.endpoint
        "COSMOS_KEY" = azurerm_cosmosdb_account.cosmosdb.primary_key
        "COSMOS_DB_NAME" = "${var.project_name}-${terraform.workspace}"
    }
}

# Create an App Service Plan
resource "azurerm_app_service_plan" "resumematchpro" {
    name                = "${var.project_name}-${terraform.workspace}-asp"
    location            = azurerm_resource_group.rg.location
    resource_group_name = azurerm_resource_group.rg.name
    kind                = "FunctionApp"
    sku {
        tier = "Dynamic"  # Dynamic means consumption plan
        size = "Y1"     # Y1 is the smallest size
    }
}


# Output Function App Name
output "FUNCTION_APP_NAME" {
    value = azurerm_function_app.resumematchpro.name
}

# Output Function App URL
output "FUNCTION_APP_URL" {
    value = azurerm_function_app.resumematchpro.default_hostname
}

# Output Function App publish profile
output "GET_PUBLISHING_PROFILE_SCRIPT" {
    value = "az functionapp deployment list-publishing-profiles --name ${azurerm_function_app.resumematchpro.name} --resource-group ${azurerm_resource_group.rg.name} --xml"
    description = "Run this command in your shell to retrieve the Azure Function App's publishing profile."
}
