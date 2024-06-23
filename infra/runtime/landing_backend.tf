# Create an Azure Function App
resource "azurerm_linux_function_app" "landing_backend" {
  name                      = "${var.project_name}-${terraform.workspace}-landing-backend"
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
      allowed_origins = ["https://${azurerm_static_web_app.landingpage.default_host_name}"]
    }

  }

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.ResumeMatchProInsights.instrumentation_key
    "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.storage.primary_connection_string
    "AzureWebJobsStorage" = azurerm_storage_account.storage.primary_connection_string
    "ALLOW_ORIGIN" = "https://${azurerm_static_web_app.landingpage.default_host_name}"
    "COSMOS_URL" = azurerm_cosmosdb_account.cosmosdb.endpoint
    "COSMOS_KEY" = azurerm_cosmosdb_account.cosmosdb.primary_key
    "COSMOS_DB_NAME" = "${var.project_name}-${terraform.workspace}-landing-backend"
  }

  lifecycle {
        ignore_changes = [
            app_settings["APPINSIGHTS_INSTRUMENTATIONKEY"],
            app_settings["AzureWebJobsStorage"]
        ]
    }

  tags = {
    environment = terraform.workspace
  }
}



# Output Function App Name
output "LANDING_BACKEND_FUNCTION_APP_NAME" {
    value = azurerm_linux_function_app.landing_backend.name
}

# Output Function App URL
# output "LANDING_BACKEND_FUNCTION_APP_URL" {
#     value = azurerm_linux_function_app.landing_backend.default_hostname
# }

# Output Function App publish profile
output "LANDING_BACKEND_GET_PUBLISHING_PROFILE_SCRIPT" {
    value = "az functionapp deployment list-publishing-profiles --name ${azurerm_linux_function_app.landing_backend.name} --resource-group ${azurerm_resource_group.rg.name} --xml"
    description = "Run this command in your shell to retrieve the Azure Function App's publishing profile."
}
