# Define variables
variable "project_name" {
    description = "Name of the project, used in resource naming"
    type        = string
    default     = "resumematchpro"
}

variable "environment_name" {
    type    = string
    default = "dev"
}

variable "location" {
    description = "The Azure region where resources will be created"
    type        = string
    default     = "uaenorth"
}

variable "europe_location" {
    type    = string
    default = "West Europe"
}

variable "domain_name" {
    description = "Domain name for the application"
    type        = string
    default     = "resumematch.pro"
}

variable "b2c_tenant" {
    description = "Azure AD B2C tenant name"
    type        = string
    default     = "resumematchprodev"
}

# Azure AD B2C Configuration
variable "B2C_TENANT_DOMAIN_NAME" {
    description = "Azure AD B2C Tenant domain name (e.g., 'resumematchprodev.onmicrosoft.com')"
    type        = string
}

variable "B2C_TENANT_NAME" {
    description = "Azure AD B2C Tenant name without domain (e.g., 'resumematchprodev')"
    type        = string
}

variable "BACKEND_B2C_CLIENT_ID" {
    description = "Azure AD B2C Application (client) ID for the main backend API"
    type        = string
}

# variable "BACKEND_B2C_CLIENT_SECRET" {
#     description = "Azure AD B2C Client Secret for the main backend API"
#     type        = string
#     sensitive   = true
# }

# OpenAI Configuration
variable "AZURE_OPENAI_API_KEY" {
    description = "Azure OpenAI API Key"
    type        = string
    sensitive   = true
}

variable "AZURE_OPENAI_ENDPOINT" {
    description = "Azure OpenAI Endpoint"
    type        = string
}

variable "AZURE_OPENAI_DEPLOYMENT_NAME" {
    description = "Azure OpenAI Deployment Name"
    type        = string
}

# Document Intelligence Configuration
variable "AZURE_DOCUMENT_INTELLIGENCE_KEY" {
    description = "Azure Document Intelligence Key"
    type        = string
    sensitive   = true
}

variable "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" {
    description = "Azure Document Intelligence Endpoint"
    type        = string
}

# CORS Configuration
variable "MAIN_FRONTEND_URLS" {
    description = "Comma-separated list of allowed origins for main frontend"
    type        = string
}

variable "LANDING_FRONTEND_URLS" {
    description = "Comma-separated list of allowed origins for landing frontend"
    type        = string
}

# Automatically detect workspace
locals {
    env = terraform.workspace
}

variable "DIRECTORY_ID" {
    description = "The directory (tenant) ID of the Azure AD B2C tenant"
    type        = string
}
