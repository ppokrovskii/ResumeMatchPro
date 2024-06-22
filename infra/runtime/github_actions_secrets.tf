data "external" "publishing_profile" {
  program = ["powershell", "-File", "./fetch_publishing_profile.ps1", azurerm_linux_function_app.landing_backend.name, azurerm_resource_group.rg.name]

  # No input is required, so this can be an empty map
  query = {}
}

# Convert the publishing profile from JSON string to raw string
locals {
  publishing_profile = data.external.publishing_profile.result.publishing_profile
}

data "github_repository" "repo" {
  full_name = "ppokrovskii/ResumeMatchPro"
}

resource "github_repository_environment" "repo_environment" {
  repository  = data.github_repository.repo.name
  environment = terraform.workspace
}

resource "github_actions_environment_secret" "LANDING_BACKEND_PUBLISHING_PROFILE" {
  repository      = data.github_repository.repo.name
  environment     = github_repository_environment.repo_environment.environment
  secret_name     = "LANDING_BACKEND_PUBLISHING_PROFILE"
  plaintext_value = local.publishing_profile
}

# data "github_repository" "repo" {
#   full_name = "ppokrovskii/ResumeMatchPro"
# }

# resource "github_repository_environment" "repo_environment" {
#   repository       = data.github_repository.repo.name
#   environment      = terraform.workspace
# }

# resource "github_actions_environment_secret" "LANDING_BACKEND_PUBLISHING_PROFILE" {
#   repository       = data.github_repository.repo.name
#   environment      = github_repository_environment.repo_environment.environment
#   secret_name      = "LANDING_BACKEND_PUBLISHING_PROFILE"
#   plaintext_value  = "az functionapp deployment list-publishing-profiles --name ${azurerm_linux_function_app.landing_backend.name} --resource-group ${azurerm_resource_group.rg.name} --xml"
# }
