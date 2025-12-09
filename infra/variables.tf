variable "project_id" {
    description = "The Gooogle Project ID"
    type = string
    default = "backend-project-480607"
}

variable "region" {
    description = "Gooogle Cloud Region"
    type = string
    default = "me-west1"
}


variable "app_name" {
    description = "The name of our application"
    type = string
    default = "backend-api"
}

variable "zone" {
  description = "Google Cloud Zone"
  type        = string
  default     = "me-west1-a"
}