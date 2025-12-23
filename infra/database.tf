# 1. Random ID for Unique Naming
# Cloud SQL instance names are globally unique and cannot be reused immediately after deletion.
# Adding a random suffix ensures we don't get naming conflicts.
resource "random_id" "db_name_suffix" {
  byte_length = 4
}

# 2. Cloud SQL Instance (The Server)
resource "google_sql_database_instance" "main" {
  name             = "${var.app_name}-db-${random_id.db_name_suffix.hex}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-f1-micro" # Smallest tier to save costs (Development only)
    disk_type         = "PD_SSD"
    disk_size         = 10
    availability_type = "ZONAL" # Single zone is cheaper than High Availability (HA)

    ip_configuration {
      ipv4_enabled    = false # Security: No public IP address.
      private_network = google_compute_network.vpc.id
    }
  }

  # For production, set this to true to prevent accidental data loss
  deletion_protection = false

  # CRITICAL: We must wait for the Private VPC Connection (defined in network.tf)
  # to be fully established before creating the database instance.
  depends_on = [google_service_networking_connection.private_vpc_connection]
}

# 3. Database (Logical DB)
# The actual database created inside the SQL instance.
resource "google_sql_database" "database" {
  name     = "backend_db"
  instance = google_sql_database_instance.main.name
}

# 4. Database User
# The user credentials used by the API to connect.
resource "google_sql_user" "users" {
  name     = "postgres_user"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}