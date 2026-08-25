###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/iam_bindings/outputs.tf
###############################################################################

output "data_loader_sa_email" {
  description = "Email of the data loader service account."
  value       = google_service_account.data_loader.email
}

output "analytics_viewer_sa_email" {
  description = "Email of the analytics viewer service account."
  value       = google_service_account.analytics_viewer.email
}

output "runtime_sa_email_passthrough" {
  description = "Runtime service account email, passed through for convenience."
  value       = var.runtime_sa_email
}
