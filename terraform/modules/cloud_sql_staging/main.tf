###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/cloud_sql_staging/main.tf
# Purpose   : Private PostgreSQL instance backing the Django staging service.
#
#             Security controls:
#               - Private IP only: no public address exists to attack.
#               - Identity and Access Management database authentication:
#                 there is no database password anywhere - the runtime
#                 service account authenticates with its Google identity.
#               - Automated daily backups with one day of transaction log
#                 retention for point-in-time recovery.
#               - Deletion protection and a locked maintenance window.
#               - Data at rest uses Google-managed encryption (Customer-
#                 Managed upgrade path recorded in docs/decisions.md).
#
#             Networking: a dedicated Virtual Private Cloud with one regional
#             subnet, Private Services Access peering for Cloud SQL, and a
#             Serverless VPC Access connector so App Engine standard reaches
#             the private address.
###############################################################################

resource "google_compute_network" "staging" {
  project                         = var.project_id
  name                            = "${var.name_prefix}-network"
  auto_create_subnetworks         = false
  delete_default_routes_on_create = false
}

resource "google_compute_subnetwork" "staging" {
  project       = var.project_id
  name          = "${var.name_prefix}-subnet"
  region        = var.region
  network       = google_compute_network.staging.id
  ip_cidr_range = var.subnet_cidr

  private_ip_google_access = true
}

# Address range reserved for Private Services Access so Cloud SQL attaches
# inside the VPC instead of on the public internet.
resource "google_compute_global_address" "psa_range" {
  project       = var.project_id
  name          = "${var.name_prefix}-psa-range"
  purpose       = "VPC_PEERING"
  prefix_length = var.psa_prefix_length
  address_type  = "INTERNAL"

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_service_networking_connection" "psa" {
  network                 = google_compute_network.staging.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.psa_range.name]
}

resource "google_vpc_access_connector" "app_engine_connector" {
  project = var.project_id
  name    = "${var.name_prefix}-connector"
  region  = var.region
  network = google_compute_network.staging.name

  # A dedicated /28 inside the subnet space for the connector.
  ip_cidr_range = var.connector_cidr

  min_instances = 2
  max_instances = 4

  depends_on = [google_compute_subnetwork.staging]
}

resource "google_sql_database_instance" "postgres" {
  project          = var.project_id
  name             = "${var.name_prefix}-postgres"
  database_version = "POSTGRES_16"
  region           = var.region

  deletion_protection = true

  settings {
    tier              = "db-g1-small"
    availability_type = "ZONAL"
    disk_autoresize   = true
    disk_size         = 10

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      transaction_log_retention_days = 1
    }

    maintenance_window {
      day  = 7
      hour = 4
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.staging.id

      # Passwordless posture: only Identity and Access Management logins.
      ssl_mode = "ENCRYPTED_ONLY"
    }

    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }

  depends_on = [google_service_networking_connection.psa]
}

resource "google_sql_database" "onboarding" {
  project  = var.project_id
  name     = "onboarding_staging"
  instance = google_sql_database_instance.postgres.name
}

# Passwordless database user bound to the runtime service account identity.
# The account identifier for service accounts omits the .gserviceaccount.com
# suffix per Cloud SQL Identity and Access Management authentication rules.
resource "google_sql_user" "runtime_iam_user" {
  project  = var.project_id
  name     = replace(var.runtime_sa_email, ".gserviceaccount.com", "")
  instance = google_sql_database_instance.postgres.name
  type     = "CLOUD_IAM_SERVICE_ACCOUNT"
}
