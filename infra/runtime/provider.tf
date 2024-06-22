provider "azurerm" {
    features {}
}

provider "github" {
    token = var.github_token
    owner = var.github_owner
}

terraform {
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "~> 3.108.0"
        }
        github = {
            source = "integrations/github"
            version = "~> 6.0"
        }
    }
}

variable "github_token" {
  description = "GitHub token with appropriate permissions"
  type        = string
  sensitive   = true
}

variable "github_owner" {
    description = "The GitHub organization or user name"
}