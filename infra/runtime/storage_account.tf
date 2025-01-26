# Create Blob Storage
resource "azurerm_storage_account" "storage" {
    name                     = "rmp${terraform.workspace}"
    resource_group_name      = azurerm_resource_group.rg.name
    location                 = var.location
    account_tier             = "Standard"  
    account_replication_type = "LRS"  # Locally redundant storage
    account_kind            = "StorageV2"
    enable_https_traffic_only = true
    min_tls_version         = "TLS1_2"
    access_tier             = "Hot"
    
    tags = {
        environment = "${terraform.workspace}"
    }

    lifecycle {
        ignore_changes = [
            location,  # Ignore location changes
            tags,  # Ignore changes to tags
            account_kind,  # Ignore changes to account kind
            access_tier,  # Ignore changes to access tier
            enable_https_traffic_only,  # Ignore changes to HTTPS only
            min_tls_version,  # Ignore changes to TLS version
            network_rules,  # Ignore changes to network rules
            blob_properties,  # Ignore changes to blob properties
            queue_properties,  # Ignore changes to queue properties
            share_properties,  # Ignore changes to share properties
            static_website  # Ignore changes to static website
        ]
    }
}

# Output Blob Storage connection string
output "AZURE_STORAGE_CONNECTION_STRING" {
    value = azurerm_storage_account.storage.primary_connection_string
    sensitive = true
}