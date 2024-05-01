# Create an Azure Function App
resource "azurerm_linux_function_app" "resumematchpro" {
    name                      = "${var.project_name}-${terraform.workspace}-function-app"
    location                  = azurerm_resource_group.rg.location
    resource_group_name       = azurerm_resource_group.rg.name
    service_plan_id           = azurerm_service_plan.resumematchpro.id
    storage_account_name      = azurerm_storage_account.storage.name
    storage_account_access_key = azurerm_storage_account.storage.primary_access_key
    # version                   = "~3"
    # os_type                   = "linux"
    # runtime_stack             = "NODE|14-lts"

    site_config {
        application_stack {
            python_version = "3.11"
        }
    }

    app_settings = {
        "FUNCTIONS_WORKER_RUNTIME" = "python"
        # "WEBSITE_RUN_FROM_PACKAGE" = ""
        "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.ResumeMatchProInsights.instrumentation_key
        "AzureWebJobsStorage" = azurerm_storage_account.storage.primary_connection_string
        "COSMOSDB_URL" = azurerm_cosmosdb_account.cosmosdb.endpoint
        "COSMOSDB_KEY" = azurerm_cosmosdb_account.cosmosdb.primary_key
    }
}


# Create an App Service Plan
resource "azurerm_service_plan" "resumematchpro" {
    name                = "${var.project_name}-${terraform.workspace}-service-plan"
    location            = azurerm_resource_group.rg.location
    resource_group_name = azurerm_resource_group.rg.name
    os_type             = "Linux"
    sku_name            = "Y1"
    # sku {
    #     tier = "Dynamic"
    #     size = "Y1"
    # }
}


# Output Function App Name
output "FUNCTION_APP_NAME" {
    value = azurerm_linux_function_app.resumematchpro.name
}

# Output Function App URL
output "FUNCTION_APP_URL" {
    value = azurerm_linux_function_app.resumematchpro.default_hostname
}

# Output Function App publish profile
output "GET_PUBLISHING_PROFILE_SCRIPT" {
    value = "az functionapp deployment list-publishing-profiles --name ${azurerm_linux_function_app.resumematchpro.name} --resource-group ${azurerm_resource_group.rg.name} --xml"
    description = "Run this command in your shell to retrieve the Azure Function App's publishing profile."
}
