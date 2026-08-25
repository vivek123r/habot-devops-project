###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/bigquery_staged/outputs.tf
###############################################################################

output "dataset_id" {
  description = "Identifier of the D1 Staged/Enforced dataset."
  value       = google_bigquery_dataset.staged.dataset_id
}

output "dataset_location" {
  description = "Location of the D1 Staged/Enforced dataset."
  value       = google_bigquery_dataset.staged.location
}

output "enforced_table_id" {
  description = "Fully qualified identifier of the enforced-schema events table."
  value       = "${var.project_id}.${google_bigquery_dataset.staged.dataset_id}.${google_bigquery_table.enforced.table_id}"
}

output "secure_view_table_id" {
  description = "Fully qualified identifier of the Row-Level Security protected view."
  value       = "${var.project_id}.${google_bigquery_dataset.staged.dataset_id}.${google_bigquery_table.secure_view.table_id}"
}

output "secure_view_table_name" {
  description = "Plain table identifier of the Row-Level Security protected view."
  value       = google_bigquery_table.secure_view.table_id
}

output "rls_clearance_table_id" {
  description = "Fully qualified identifier of the Row-Level Security clearance allowlist table."
  value       = "${var.project_id}.${google_bigquery_dataset.staged.dataset_id}.${google_bigquery_table.rls_clearance.table_id}"
}
