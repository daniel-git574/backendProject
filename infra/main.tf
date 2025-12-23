# 1. Artifact Registry (Docker Storage)
# The private warehouse where we store our built Docker images.

resource "google_artifact_registry_repository" "my_repo" {
  location      = var.region
  repository_id = "${var.app_name}-repo"
  description   = "Docker Repository for ${var.app_name}"
  format        = "DOCKER"
}

# 2. Bastion Host
# Secure entry point to the private network via Google IAP.
# Since DB and App are private, we tunnel through this VM to access them.

resource "google_compute_instance" "bastion" {
  name         = "${var.app_name}-bastion"
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.vpc.id
    subnetwork = google_compute_subnetwork.subnet.id
    # No public IP 
  }

  # Startup Script: Installs & Configures TinyProxy for tunneling
  metadata_startup_script = <<-EOF
    #! /bin/bash
    apt-get update
    apt-get install -y tinyproxy
    sed -i 's/Allow 127.0.0.1/Allow localhost/' /etc/tinyproxy/tinyproxy.conf
    systemctl restart tinyproxy
  EOF

  tags = ["bastion-host"]

  service_account {
    scopes = ["cloud-platform"]
  }
}





