locals {
  domain_name = terraform.workspace == "prod" ? "resumematch.pro" : "${terraform.workspace}.resumematch.pro"
}

resource "azurerm_resource_group" "resumematchpro_dns_rg" {
    name     = "resumematchpro-dns-rg"
    location = var.location
}

resource "azurerm_dns_zone" "dns_zone" {
  name                = "resumematch.pro"
  resource_group_name = azurerm_resource_group.resumematchpro_dns_rg.name  # I don't use azurerm_resource_group.rg here to have same dns zone for all envs
}

# Custom domain for prod environment (root domain)
resource "azurerm_static_web_app_custom_domain" "prod_custom_domain" {  # azurerm_static_web_app_custom_domain.prod_custom_domain[0]
  count               = terraform.workspace == "prod" ? 1 : 0
  static_web_app_id   = azurerm_static_web_app.landingpage.id
  domain_name         = azurerm_dns_zone.dns_zone.name
  validation_type     = "dns-txt-token"
}

# DNS TXT record for apex domain validation (prod only, one time only for validatoin and custom domain setup)
# resource "azurerm_dns_txt_record" "apex_domain_validation" {
#   count               = terraform.workspace == "prod" ? 1 : 0
#   name                = "@"
#   zone_name           = azurerm_dns_zone.dns_zone.name
#   resource_group_name = azurerm_resource_group.resumematchpro_dns_rg.name
#   ttl                 = 300
#   record {
#     value = azurerm_static_web_app_custom_domain.prod_custom_domain[count.index].validation_token
#   }
#   depends_on = [azurerm_static_web_app_custom_domain.prod_custom_domain]
# }



# DNS A record for prod environment (root domain)
resource "azurerm_dns_a_record" "prod_a_record" {
  count               = terraform.workspace == "prod" ? 1 : 0
  name                = "@"
  zone_name           = azurerm_dns_zone.dns_zone.name
  resource_group_name = azurerm_resource_group.resumematchpro_dns_rg.name
  ttl                 = 300
  target_resource_id  = azurerm_static_web_app.landingpage.id
}

# Custom domain for dev environment (subdomain)
resource "azurerm_static_web_app_custom_domain" "dev_custom_domain" {
  count               = terraform.workspace != "prod" ? 1 : 0
  static_web_app_id   = azurerm_static_web_app.landingpage.id
  domain_name         = local.domain_name
  validation_type     = "cname-delegation"
}

# DNS CNAME record for dev environment (subdomain)
resource "azurerm_dns_cname_record" "dev_cname_record" {
  count               = terraform.workspace != "prod" ? 1 : 0
  name                = "dev"
  zone_name           = azurerm_dns_zone.dns_zone.name
  resource_group_name = azurerm_resource_group.resumematchpro_dns_rg.name
  ttl                 = 300
  record              = azurerm_static_web_app.landingpage.default_host_name
}

# DNS TXT record for apex domain validation (dev only)
# resource "azurerm_dns_txt_record" "dev_domain_validation" {
#   count               = terraform.workspace != "prod" ? 1 : 0
#   name                = "dev"
#   zone_name           = azurerm_dns_zone.dns_zone.name
#   resource_group_name = azurerm_resource_group.resumematchpro_dns_rg.name
#   ttl                 = 300
#   record {
#     value = azurerm_static_web_app_custom_domain.dev_custom_domain[count.index].validation_token
#   }
# }

output "DNS_SERVERS_SCRIPT" {
    value = "az network dns zone show --resource-group ${azurerm_resource_group.resumematchpro_dns_rg.name} --name ${azurerm_dns_zone.dns_zone.name} --query nameServers"  # --output tsv
    description = "Run this command in your shell to retrieve the DNS zone's name servers."
}
