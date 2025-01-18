# Create the backend application registration
resource "azuread_application" "backend" {
  display_name     = "ResumeMatchPro-Backend"
  identifier_uris  = ["https://resumematchprodev.onmicrosoft.com/resumematchpro-api"]
  sign_in_audience = "AzureADandPersonalMicrosoftAccount"
  tags             = ["notApiConsumer", "webApi"]

  web {
    redirect_uris = [
      # Azure Development environment
      "https://resumematchpro-dev-function-app.azurewebsites.net/.auth/login/aad/callback",
      # Development tools
      "https://oauth.pstmn.io/v1/callback",
      # Local development environment
      "http://localhost:7071/.auth/login/aad/callback",
      "http://localhost:3000/auth-callback/"
    ]
    implicit_grant {
      access_token_issuance_enabled = false
      id_token_issuance_enabled     = false
    }
  }

  # Required resource access (Microsoft Graph permissions)
  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph

    resource_access {
      id   = "37f7f235-527c-4136-accd-4a02d197296e"
      type = "Scope"
    }
    resource_access {
      id   = "7427e0e9-2fba-42fe-b0c0-848c9e6a8182"
      type = "Scope"
    }
  }

  # Expose API scopes
  api {
    mapped_claims_enabled          = true
    requested_access_token_version = 2

    # Default scope that doesn't require admin consent
    oauth2_permission_scope {
      admin_consent_description  = "Allow the application to access ResumeMatchPro API on behalf of the user"
      admin_consent_display_name = "Access ResumeMatchPro API"
      enabled                   = true
      id                        = "da4b6fe1-620b-4d9c-9550-3d8fa01afedb"
      type                      = "User"
      user_consent_description  = "Allow the application to access ResumeMatchPro API on your behalf"
      user_consent_display_name = "Access ResumeMatchPro API"
      value                     = "Files.ReadWrite"
    }
  }
}

# Create the frontend application registration
resource "azuread_application" "frontend" {
  display_name     = "ResumeMatchPro-Frontend"
  sign_in_audience = "AzureADandPersonalMicrosoftAccount"
  fallback_public_client_enabled = true
  tags             = ["apiConsumer", "singlePageApp"]
  
  api {
    requested_access_token_version = 2
  }

  # Configure as public client application
  public_client {
    redirect_uris = []  # Empty as per current Azure state
  }

  # Configure as single page application
  single_page_application {
    redirect_uris = [
      # Local development environment
      "http://localhost:3000/",
      "http://localhost:3000/auth-callback/",
      # Development environment
      "https://app.dev.resumematch.pro/",
      "https://app.dev.resumematch.pro/auth-callback/"
    ]
  }

  # Required resource access (Microsoft Graph permissions)
  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph

    # OpenID permissions
    resource_access {
      id   = "37f7f235-527c-4136-accd-4a02d197296e" # openid
      type = "Scope"
    }
    # Profile permissions
    resource_access {
      id   = "14dad69e-099b-42c9-810b-d002981feec1" # profile
      type = "Scope"
    }
    # Offline access permissions
    resource_access {
      id   = "7427e0e9-2fba-42fe-b0c0-848c9e6a8182" # offline_access
      type = "Scope"
    }
  }

  # Required resource access (to access our backend API)
  required_resource_access {
    resource_app_id = azuread_application.backend.application_id

    resource_access {
      id   = [for scope in azuread_application.backend.api[0].oauth2_permission_scope : scope.id if scope.value == "Files.ReadWrite"][0]
      type = "Scope"
    }
  }
}

# Create service principal for the backend
resource "azuread_service_principal" "backend" {
  client_id = azuread_application.backend.client_id
}

# Create service principal for the frontend
resource "azuread_service_principal" "frontend" {
  client_id = azuread_application.frontend.client_id
}

# Pre-authorize the frontend application to access the backend API
resource "azuread_application_pre_authorized" "frontend_backend" {
  application_id       = azuread_application.backend.id
  authorized_client_id = azuread_application.frontend.client_id
  permission_ids      = [for scope in azuread_application.backend.api[0].oauth2_permission_scope : scope.id if scope.value == "Files.ReadWrite"]
}

# Output the application IDs and other important information
output "backend_application_id" {
  value = azuread_application.backend.application_id
}

output "frontend_application_id" {
  value = azuread_application.frontend.application_id
}

output "backend_scope" {
  value = "api://resumematchpro-backend-api/Files.ReadWrite"
}

# Output B2C Authentication URLs
output "B2C_AUTH_URL" {
    value = "https://${var.B2C_TENANT_NAME}.b2clogin.com/${var.B2C_TENANT_NAME}.onmicrosoft.com/B2C_1_signupsignin/oauth2/v2.0/authorize"
    description = "Use this URL for OAuth2 authorization in Postman"
}

output "B2C_TOKEN_URL" {
    value = "https://${var.B2C_TENANT_NAME}.b2clogin.com/${var.B2C_TENANT_NAME}.onmicrosoft.com/B2C_1_signupsignin/oauth2/v2.0/token"
    description = "Use this URL for OAuth2 token endpoint in Postman"
}

output "B2C_SCOPE" {
    value = "openid offline_access https://${var.B2C_TENANT_NAME}.onmicrosoft.com/${var.BACKEND_API_CLIENT_ID}/user_impersonation"
    description = "Use this scope for OAuth2 configuration in Postman"
} 