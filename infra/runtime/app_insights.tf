// Add data source to fetch the Log Analytics workspace
data "azurerm_log_analytics_workspace" "app_insights_workspace" {
  name                = "managed-${var.project_name}-${terraform.workspace}-ResumeMatchProInsights-ws"
  resource_group_name = "ai_${var.project_name}-${terraform.workspace}-resumematchproinsight_${var.log_analytics_workspace_suffix}"
}

resource "azurerm_application_insights" "ResumeMatchProInsights" {
    name                = "${var.project_name}-${terraform.workspace}-ResumeMatchProInsights"
    location            = var.location
    resource_group_name = azurerm_resource_group.rg.name
    application_type    = "web"
    daily_data_cap_in_gb = 1
    retention_in_days = 30

    lifecycle {
        ignore_changes = [
            workspace_id
        ]
    }
}

resource "azurerm_monitor_action_group" "telegram_alerts" {
    name = "${var.project_name}-${terraform.workspace}-telegram-alerts"
    resource_group_name = azurerm_resource_group.rg.name
    short_name = "tg-alerts"
    
    webhook_receiver {
        name = "telegram-webhook"
        service_uri = "https://${azurerm_linux_function_app.telegram_alert_function.name}.azurewebsites.net/api/telegram-webhook?code=${var.TELEGRAM_FUNCTION_KEY}"
        use_common_alert_schema = true
    }

}

resource "azurerm_monitor_metric_alert" "failed_requests_alert" {
    name = "${var.project_name}-${terraform.workspace}-failed-requests-alert"
    resource_group_name = azurerm_resource_group.rg.name
    scopes = [azurerm_application_insights.ResumeMatchProInsights.id]
    description = "Alert when the number of failed requests exceeds a threshold"
    severity = 3
    frequency = "PT1M"
    window_size = "PT15M"

    criteria {
        metric_namespace = "Microsoft.Insights/components"
        metric_name = "requests/failed"
        aggregation = "Count"
        operator = "GreaterThan"
        threshold = 0        
    }

    action {
        action_group_id = azurerm_monitor_action_group.telegram_alerts.id
    }

    enabled = true
    
}

resource "azurerm_monitor_metric_alert" "exceptions_alert" {
    name = "${var.project_name}-${terraform.workspace}-exceptions-alert"
    resource_group_name = azurerm_resource_group.rg.name
    scopes = [azurerm_application_insights.ResumeMatchProInsights.id]
    description = "Alert when exceptions or errors occur in the application"
    severity = 2
    frequency = "PT1M"
    window_size = "PT5M"

    dynamic_criteria {
        metric_namespace = "Microsoft.Insights/components"
        metric_name = "exceptions/server"
        aggregation = "Count"
        operator = "GreaterThan"
        alert_sensitivity = "High"
        evaluation_total_count = 1
        evaluation_failure_count = 1
    }

    action {
        action_group_id = azurerm_monitor_action_group.telegram_alerts.id
    }

    enabled = true
}

resource "azurerm_monitor_metric_alert" "error_traces_alert" {
    name = "${var.project_name}-${terraform.workspace}-error-traces-alert"
    resource_group_name = azurerm_resource_group.rg.name
    scopes = [azurerm_application_insights.ResumeMatchProInsights.id]
    description = "Alert when error traces are detected"
    severity = 2
    frequency = "PT1M"
    window_size = "PT5M"

    criteria {
        metric_namespace = "Microsoft.Insights/components"
        metric_name = "traces/count"
        aggregation = "Count"
        operator = "GreaterThan"
        threshold = 0
        dimension {
            name = "severityLevel"
            operator = "Include"
            values = ["3"]  # Error level
        }
    }

    action {
        action_group_id = azurerm_monitor_action_group.telegram_alerts.id
    }

    enabled = true
}

output "APP_INSIGHTS_INSTRUMENTATION_KEY" {
    value = azurerm_application_insights.ResumeMatchProInsights.instrumentation_key
    sensitive = true
}
