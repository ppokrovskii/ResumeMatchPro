resource "azurerm_linux_function_app" "telegram_alert_function" {
    name = "${var.project_name}-${terraform.workspace}-telegram-alert-function"
    location                  = azurerm_resource_group.rg.location
    resource_group_name       = azurerm_resource_group.rg.name
    service_plan_id           = azurerm_service_plan.resumematchpro.id
    storage_account_name      = azurerm_storage_account.storage.name
    storage_account_access_key = azurerm_storage_account.storage.primary_access_key

    app_settings = {
        "FUNCTIONS_WORKER_RUNTIME" = "python"
        # "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.ResumeMatchProInsights.instrumentation_key
        "APPLICATIONINSIGHTS_CONNECTION_STRING" = azurerm_application_insights.ResumeMatchProInsights.connection_string
        "APPINSIGHTS_ENABLED" = "true"
        "APPINSIGHTS_SNAPSHOTFEATURE_VERSION" = "1.0"
        "APPINSIGHTS_DISABLE_QUICKPULSE" = "false"
        "TELEGRAM_BOT_TOKEN" = var.TELEGRAM_BOT_TOKEN
        "TELEGRAM_CHAT_ID" = var.TELEGRAM_CHAT_ID
    }

    site_config {
        application_stack {
            python_version = "3.11"
        }
        cors {
            allowed_origins = split(",", "https://portal.azure.com")
            support_credentials = true
        }
    }
}

