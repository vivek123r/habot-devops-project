###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/cloud_sql_staging/outputs.tf
###############################################################################

output "instance_connection_name" {
  description = "Connection string used by clients and the App Engine Unix socket."
  value       = google_sql_database_instance.postgres.connection_name
}

output "instance_private_ip" {
  description = "Private address of the instance; no public address exists."
  value       = google_sql_database_instance.postgres.private_ip_address
}

output "database_name" {
  description = "Name of the onboarding application database."
  value       = google_sql_database.onboarding.name
}

output "network_name" {
  description = "Name of the staging Virtual Private Cloud network."
  value       = google_compute_network.staging.name
}
