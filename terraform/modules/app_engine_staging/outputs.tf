###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/app_engine_staging/outputs.tf
###############################################################################

output "runtime_sa_email" {
  description = "Email address of the dedicated runtime service account."
  value       = google_service_account.runtime.email
}

output "application_url" {
  description = "Public HTTPS entry point of the staging application."
  value       = "https://${var.project_id}.appspot.com"
}

output "app_engine_location" {
  description = "Effective App Engine location code."
  value       = google_app_engine_application.staging.location_id
}
