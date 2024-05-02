# Create Cosmos DB
resource "azurerm_cosmosdb_account" "cosmosdb" {
    name                = "${var.project_name}-${terraform.workspace}-cosmosdb"
    location            = azurerm_resource_group.rg.location
    resource_group_name = azurerm_resource_group.rg.name
    offer_type          = "Standard"
    geo_location {
        location          = azurerm_resource_group.rg.location
        failover_priority = 0 # The first region to failover to
    }

    # geo_location {
    #     location          = "East US"
    #     failover_priority = 1 # The second region to failover to
    # }

    consistency_policy {
        consistency_level = "Session"  # Strong, BoundedStaleness, Session, or Eventual
    }
}

# Output Cosmos DB connection string
output "COSMOS_URL" {
    value = azurerm_cosmosdb_account.cosmosdb.endpoint
}

output "COSMOS_KEY" {
    value = azurerm_cosmosdb_account.cosmosdb.primary_key
    sensitive = true
}