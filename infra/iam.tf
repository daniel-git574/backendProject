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