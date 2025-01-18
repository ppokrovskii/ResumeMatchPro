terraform {
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "~> 3.108.0"
        }
        azuread = {
            source  = "hashicorp/azuread"
            version = "~> 2.53.0"
        }
    }
}

provider "azuread" {
    tenant_id = "9fe31206-ac65-4e49-966c-0c07561ca0f9"  # neoteq.dev tenant
}

provider "azurerm" {
    features {}
    tenant_id = "9fe31206-ac65-4e49-966c-0c07561ca0f9"  # neoteq.dev tenant
    skip_provider_registration = true
}