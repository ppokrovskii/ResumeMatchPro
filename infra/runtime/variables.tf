# Define variables
variable "project_name" {
    type    = string
    default = "resumematchpro"
}

variable "environment_name" {
    type    = string
    default = "dev"
}

variable "location" {
    type    = string
    default = "UAE North"
}

variable "europe_location" {
    type    = string
    default = "West Europe"
}

# Azure AD B2C Configuration
variable "BACKEND_B2C_CLIENT_ID" {
    description = "Azure AD B2C Application (client) ID for the main backend API"
    type        = string
}

variable "B2C_TENANT_NAME" {
    description = "Azure AD B2C Tenant name (e.g., 'resumematchprodev' or 'resumematchpro')"
    type        = string
}

variable "BACKEND_B2C_CLIENT_SECRET" {
    description = "Azure AD B2C Client Secret for the main backend API"
    type        = string
    sensitive   = true
}

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
