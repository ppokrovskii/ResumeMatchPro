resource "azurerm_application_insights" "ResumeMatchProInsights" {
    name                = "${var.project_name}-${terraform.workspace}-ResumeMatchProInsights"
    location            = var.location
    resource_group_name = azurerm_resource_group.rg.name
    application_type    = "other"  # other is for general application insights
    daily_data_cap_in_gb = 1

    retention_in_days = 30
}

output "APP_INSIGHTS_INSTRUMENTATION_KEY" {
    value = azurerm_application_insights.ResumeMatchProInsights.instrumentation_key
    sensitive = true
}
