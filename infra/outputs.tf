# Useful information displayed in the terminal after 'terraform apply'.

output "api_url" {
  description = "The internal Cloud Run URL (Accessible only via Bastion)."
  value       = google_cloud_run_v2_service.api.uri
}

output "db_private_ip" {
  description = "The Private IP address of the Cloud SQL instance."
  value       = google_sql_database_instance.main.private_ip_address
}

output "bastion_tunnel_command" {
  description = "Run this command to open the SSH tunnel to your DB:"
  # Generates the exact command, including the correct IP!
  value = "gcloud compute ssh ${google_compute_instance.bastion.name} --project=${var.project_id} --zone=${var.zone} --ssh-flag=\"-L 5437:${google_sql_database_instance.main.private_ip_address}:5432\""
}