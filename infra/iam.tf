# 1. Createing the Service Account for the API application
resource "google_service_account" "api_sa" {
  account_id = "${var.app_name}-api-sa"

  # A human-readable name displayed in the Google Cloud Console
  display_name = "Service Account for Daniel's Backend API"
}

# 2. Grant Permission A: Cloud SQL Client
# Allows the Service Account to connect to Cloud SQL instances.
resource "google_project_iam_member" "api_sa_sql_client" {
  project = var.project_id

  # The specific IAM role for SQL connectivity
  role = "roles/cloudsql.client"

  # The Member: reference the email of the SA created above.
  # Note: IAM requires the "serviceAccount:" prefix before the email.
  member = "serviceAccount:${google_service_account.api_sa.email}"
}

# 3. Grant Permission B: Log Writer
# Allows the Service Account to write logs to Cloud Logging.
resource "google_project_iam_member" "api_sa_logging" {
  project = var.project_id

  role = "roles/logging.logWriter"

  # Using the same SA email reference here.
  member = "serviceAccount:${google_service_account.api_sa.email}"
}


# 4. Grant Permission C: Artifact Registry Reader 
# This allows Cloud Run (which uses api_sa) to PULL images from the Proxy.
resource "google_artifact_registry_repository_iam_member" "api_sa_artifact_reader" {
  # 1. Reference the repository defined in main.tf 
  project    = google_artifact_registry_repository.docker_hub_proxy.project
  location   = google_artifact_registry_repository.docker_hub_proxy.location
  repository = google_artifact_registry_repository.docker_hub_proxy.name

  # 2. The Role: "Reader" (Can only pull/read images)
  role = "roles/artifactregistry.reader"

  # 3. Using the same SA email reference here.
  member = "serviceAccount:${google_service_account.api_sa.email}"
}

# 5. Grant Permission D: Standard Repository Reader (For Manual Pushes)

resource "google_artifact_registry_repository_iam_member" "api_sa_standard_repo_reader" {
  project    = google_artifact_registry_repository.my_repo.project
  location   = google_artifact_registry_repository.my_repo.location
  repository = google_artifact_registry_repository.my_repo.name

  # The Role: Reader
  role = "roles/artifactregistry.reader"

  # The Member: Our trusted robot
  member = "serviceAccount:${google_service_account.api_sa.email}"
}


# 6. Cloud Run Service Agent
# Fetch the Project Number to construct the Google Robot's email
data "google_project" "project" {}

resource "google_artifact_registry_repository_iam_member" "cloud_run_agent_reader" {
  project    = google_artifact_registry_repository.docker_hub_proxy.project
  location   = google_artifact_registry_repository.docker_hub_proxy.location
  repository = google_artifact_registry_repository.docker_hub_proxy.name

  role = "roles/artifactregistry.reader"

  # Constructing the email of the Cloud Run Service Agent
  member = "serviceAccount:service-${data.google_project.project.number}@serverless-robot-prod.iam.gserviceaccount.com"
}
