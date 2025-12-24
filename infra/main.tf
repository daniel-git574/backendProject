# ARTIFACT REGISTRIES
# A. Standard Repository(Private Storage)
resource "google_artifact_registry_repository" "my_repo" {
  location      = var.region
  repository_id = "${var.app_name}-repo"
  description   = "Docker Repository for ${var.app_name}"
  format        = "DOCKER"
}

# B. Remote Repository (Docker Hub Proxy)

resource "google_artifact_registry_repository" "docker_hub_proxy" {
  location = var.region

  # Repository ID: The name of this repo in the URL
  repository_id = "docker-hub-remote"

  format = "DOCKER"

  description = "Proxy cache for Docker Hub"

  # Mode tells GCP that this is not a standard storage bucket.
  mode = "REMOTE_REPOSITORY"

  # This block defines where to fetch images from.
  remote_repository_config {
    description = "Upstream connection to public Docker Hub"

    docker_repository {
      public_repository = "DOCKER_HUB"
    }
  }
}

# 2. BASTION HOST (SECURE ACCESS)
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
    # No public IP assigned here for security
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