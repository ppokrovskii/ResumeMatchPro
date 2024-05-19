resource "azurerm_static_web_app" "landingpage" {
  name                = "landingpage"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.europe_location  # location 'uaenorth' is not available for resource type 'Microsoft.Web/staticSites'. List of available regions for the resource type is 'westus2,centralus,eastus2,westeurope,eastasia'.
}

output static_web_app_api_key {
  value = azurerm_static_web_app.landingpage.api_key
  sensitive = true
  description = "API key for the static web app"
}

output static_web_app_url {
  value = azurerm_static_web_app.landingpage.default_host_name
  description = "URL for the static web app"
}