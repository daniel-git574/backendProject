resource "google_project_service" "registry_api" {
    service = "artifactregistry.googleapis.com"
    disable_on_destroy = false
}



resource "google_project_service" "run_api" {
    service = "run.googleapis.com"
    disable_on_destroy = false
}


resource "google_artifact_registry_repository" "my_repo" {
    location = var.region
    repository_id = "${var.app_name}-repo"
    description = "My Docker Repository"
    format = "DOCKER"

    depends_on = [google_project_service.registry_api]
}

