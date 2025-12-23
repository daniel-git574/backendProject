# Cloud Run Service (The Application Container)
resource "google_cloud_run_v2_service" "api" {
  name     = "daniel-backend-api"
  location = var.region

  # Security: Blocks public internet access.
  # Traffic is allowed only from within the VPC (e.g., via Bastion tunnel).
  ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    # SECURITY CONFIGURATION (IAM)
    # Attaching the specific Service Account created in iam.tf.
    # This ensures the container runs with "Least Privilege" (only SQL + Logs),
    service_account = google_service_account.api_sa.email
    # ---------------------------------------------------------

    containers {
      # Docker Image Location
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.app_name}-repo/backend-api:v2"

      ports {
        container_port = 8000
      }

      # --- Database Configuration ---
      env {
        name  = "POSTGRES_DB"
        value = "backend_db"
      }
      env {
        name  = "POSTGRES_USER"
        value = "postgres_user"
      }
      env {
        name  = "POSTGRES_PASSWORD"
        value = var.db_password
      }
      env {
        name  = "POSTGRES_PORT"
        value = "5432"
      }
      env {
        name = "POSTGRES_HOST"
        # Dynamically pulls the Private IP of the SQL instance defined in database.tf
        value = google_sql_database_instance.main.private_ip_address
      }

      # --- Application Secrets ---
      env {
        name  = "SECRET_KEY"
        value = "super-secret-internal-key"
      }
      env {
        name  = "ADMIN_SECRET"
        value = "SUPER_ADMIN_SECRET"
      }
      env {
        name  = "ECHO_SQL"
        value = "0"
      }
    }

    # --- Network Connection ---
    # Direct VPC Egress: Connects the container to the VPC to reach the private DB.
    vpc_access {
      network_interfaces {
        network    = google_compute_network.vpc.id
        subnetwork = google_compute_subnetwork.subnet.id
      }
      egress = "ALL_TRAFFIC"
    }
  }
}