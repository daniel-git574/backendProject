# 1. PROJECT IDENTIFICATION:
variable "project_id" {
  description = "The Google Cloud Project ID (Unique Identifier)"
  type        = string
  default     = "mod-gcp-white-soi-dev-1"
}

# 2. LOCATION & REGION:
variable "region" {
  description = "Google Cloud Region for all resources (Latency & Data Residency)"
  type        = string
  default     = "me-west1"
}

variable "zone" {
  description = "Google Cloud Zone within the Region (Availability Zone)"
  type        = string
  default     = "me-west1-a"
}

# 3. APPLICATION CONFIGURATION:
variable "app_name" {
  description = "Prefix for all resources to identify them as Daniel's Terraform project"
  type        = string
  default     = "daniel-tf"
}

# 4. SECRETS & SECURITY:
variable "db_password" {
  description = "The password for the PostgreSQL user"
  type        = string
  sensitive   = true               # Prevents password from showing in logs
  default     = "MySecretPass123!" # Default password for development only
}