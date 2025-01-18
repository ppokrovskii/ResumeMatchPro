terraform {
  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }
}

provider "azuread" {
  tenant_id = var.DIRECTORY_ID  # ResumeMatchPro-dev B2C tenant
} 