# copilot prompt: terraform script to create cosmos db and blob storage in azure. 
# variables: project_name and environment_name to be used for naming and tagging accross all the resources
# outputs: credentials to connect to them. 

# Create resource group
resource "azurerm_resource_group" "rg" {
    name     = "${var.project_name}-${var.environment_name}-rg"
    location = "${var.location}"
}