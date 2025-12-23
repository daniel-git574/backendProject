# 1. VPC 
# The main network container for all resources.
resource "google_compute_network" "vpc" {
  name                    = "${var.app_name}-vpc"
  auto_create_subnetworks = false # We want full control over subnets
}

# 2. Subnet
# The specific IP range where our resources (VMs, Cloud Run connector) will live.
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.app_name}-subnet"
  region        = var.region
  network       = google_compute_network.vpc.id
  ip_cidr_range = "10.0.0.0/24"

  # Critical: Allows resources without public IPs to access Google APIs (like Artifact Registry/Cloud Run)
  private_ip_google_access = true
}

# 3. Private Service Access (Peering)
# Necessary for Cloud SQL Private IP. This reserves a range and peers it with Google's network.

resource "google_compute_global_address" "private_ip_range" {
  name          = "${var.app_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}

# 4. Cloud Router & NAT
# Allows private resources (like Bastion or Cloud Run) to reach the internet (e.g., for updates)
# without exposing them to incoming traffic.

resource "google_compute_router" "router" {
  name    = "${var.app_name}-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "${var.app_name}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# 5. Firewall Rules
# Controls who can enter the network.

# Allow SSH only from Google's IAP (Identity-Aware Proxy) range.
# This keeps port 22 closed to the public internet.
resource "google_compute_firewall" "allow_iap_ssh" {
  name    = "${var.app_name}-allow-iap-ssh"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"] # Google IAP IP range
  target_tags   = ["bastion-host"]
}