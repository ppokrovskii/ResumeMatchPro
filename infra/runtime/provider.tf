provider "azurerm" {
    features {}
}

provider "github" {
    token = var.github_token
    owner = var.github_owner
    version = "~> 5.0"
}

variable "github_token" {
  description = "GitHub token with appropriate permissions"
  type        = string
  sensitive   = true
}

variable "github_owner" {
    description = "The GitHub organization or user name"
}