# Terraform Configuration Block
terraform {
  # We require the Google provider (plugin) to interact with GCP APIs
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0" # Ensures we use a stable, modern version
    }
  }
}

# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}