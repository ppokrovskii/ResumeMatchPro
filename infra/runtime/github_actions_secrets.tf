# # get landing_publishing_profile
# data "external" "landing_publishing_profile" {
#   program = ["powershell", "-File", "./fetch_publishing_profile.ps1", azurerm_linux_function_app.landing_backend.name, azurerm_resource_group.rg.name]

#   # No input is required, so this can be an empty map
#   query = {}
#   depends_on = [azurerm_linux_function_app.landing_backend]
# }

# # Convert the publishing profile from JSON string to raw string
# locals {
#   landing_publishing_profile = data.external.landing_publishing_profile.result.publishing_profile
# }

# # get azfunctions_publishing_profile
# data "external" "azfunctions_publishing_profile" {
#   program = ["powershell", "-File", "./fetch_publishing_profile.ps1", azurerm_linux_function_app.resumematchpro.name, azurerm_resource_group.rg.name]

#   # No input is required, so this can be an empty map
#   query = {}
#   depends_on = [azurerm_linux_function_app.resumematchpro]
# }

# # Convert the publishing profile from JSON string to raw string
# locals {
#   azfunctions_publishing_profile = data.external.azfunctions_publishing_profile.result.publishing_profile
# }

# data "github_repository" "repo" {
#   full_name = "ppokrovskii/ResumeMatchPro"
# }

# resource "github_repository_environment" "repo_environment" {
#   repository  = data.github_repository.repo.name
#   environment = terraform.workspace
# }

# resource "github_actions_environment_secret" "LANDING_BACKEND_PUBLISHING_PROFILE" {
#   repository      = data.github_repository.repo.name
#   environment     = github_repository_environment.repo_environment.environment
#   secret_name     = "LANDING_BACKEND_PUBLISHING_PROFILE"
#   plaintext_value = local.landing_publishing_profile
# }

# resource "github_actions_environment_secret" "AZFUNCTIONS_PUBLISHING_PROFILE" {
#   repository      = data.github_repository.repo.name
#   environment     = github_repository_environment.repo_environment.environment
#   secret_name     = "AZFUNCTIONS_PUBLISHING_PROFILE"
#   plaintext_value = local.azfunctions_publishing_profile
# }

# resource "github_actions_environment_secret" "LANDING_AZURE_STATIC_WEB_APPS_API_TOKEN" {
#   repository      = data.github_repository.repo.name
#   environment     = github_repository_environment.repo_environment.environment
#   secret_name     = "LANDING_AZURE_STATIC_WEB_APPS_API_TOKEN"
#   plaintext_value = azurerm_static_web_app.landingpage.api_key
# }

# resource "github_actions_environment_variable" "LANDING_REACT_APP_BACKEND_URL" {
#   repository      = data.github_repository.repo.name
#   environment     = github_repository_environment.repo_environment.environment
#   variable_name   = "LANDING_REACT_APP_BACKEND_URL"
#   value           = "https://${azurerm_linux_function_app.landing_backend.default_hostname}/api"
# }

# # data "github_repository" "repo" {
# #   full_name = "ppokrovskii/ResumeMatchPro"
# # }

# # resource "github_repository_environment" "repo_environment" {
# #   repository       = data.github_repository.repo.name
# #   environment      = terraform.workspace
# # }

# # resource "github_actions_environment_secret" "LANDING_BACKEND_PUBLISHING_PROFILE" {
# #   repository       = data.github_repository.repo.name
# #   environment      = github_repository_environment.repo_environment.environment
# #   secret_name      = "LANDING_BACKEND_PUBLISHING_PROFILE"
# #   plaintext_value  = "az functionapp deployment list-publishing-profiles --name ${azurerm_linux_function_app.landing_backend.name} --resource-group ${azurerm_resource_group.rg.name} --xml"
# # }
