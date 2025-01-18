# Azure AD B2C Configuration
variable "DIRECTORY_ID" {
  description = "The directory ID (tenant ID) of the Azure AD B2C tenant"
  type        = string
}

variable "B2C_TENANT_DOMAIN_NAME" {
  description = "The domain name of the Azure AD B2C tenant"
  type        = string
}

variable "B2C_TENANT_NAME" {
  description = "The name of the Azure AD B2C tenant"
  type        = string
}

variable "FRONTEND_REDIRECT_URIS" {
  description = "List of allowed redirect URIs for the frontend application"
  type        = list(string)
}

variable "BACKEND_REDIRECT_URIS" {
  description = "List of allowed redirect URIs for the backend application"
  type        = list(string)
}