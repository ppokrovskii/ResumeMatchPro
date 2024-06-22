# Create Blob Storage
resource "azurerm_storage_account" "storage" {
    name                     = "rmp${terraform.workspace}"
    resource_group_name      = azurerm_resource_group.rg.name
    location                 = azurerm_resource_group.rg.location
    account_tier             = "Standard"  
    account_replication_type = "LRS"  # Locally redundant storage
    tags = {
        environment = "${terraform.workspace}"
    }
}



# Output Blob Storage connection string
output "AZURE_STORAGE_CONNECTION_STRING" {
    value = azurerm_storage_account.storage.primary_connection_string
    sensitive = true
}