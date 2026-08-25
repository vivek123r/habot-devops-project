###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : outputs.tf
# Purpose   : Exposes exactly the identifiers downstream engineers and the CI
#             pipeline need. Nothing sensitive is exported; identities and
#             resource names only.
###############################################################################

output "raw_landing_bucket_name" {
  description = "Name of the D0 Raw Landing Google Cloud Storage bucket."
  value       = module.storage_raw_landing.bucket_name
}

output "raw_landing_bucket_url" {
  description = "Uniform Resource Identifier of the D0 Raw Landing bucket."
  value       = module.storage_raw_landing.bucket_url
}

output "staged_dataset_id" {
  description = "Identifier of the D1 Staged/Enforced BigQuery dataset."
  value       = module.bigquery_staged.dataset_id
}

output "staged_dataset_location" {
  description = "Location of the D1 Staged/Enforced BigQuery dataset."
  value       = module.bigquery_staged.dataset_location
}

output "enforced_table_id" {
  description = "Fully qualified identifier of the enforced-schema events table."
  value       = module.bigquery_staged.enforced_table_id
}

output "row_level_security_view_id" {
  description = "Fully qualified identifier of the Row-Level Security protected view."
  value       = module.bigquery_staged.secure_view_table_id
}

output "events_topic_name" {
  description = "Pub/Sub topic receiving validated student onboarding events."
  value       = module.pubsub_pipeline.topic_name
}

output "dead_letter_topic_name" {
  description = "Pub/Sub dead-letter topic quarantining messages that fail delivery."
  value       = module.pubsub_pipeline.dlq_topic_name
}

output "runtime_service_account_email" {
  description = "Service account identity used by the App Engine staging service."
  value       = module.app_engine_staging.runtime_sa_email
}

output "data_loader_service_account_email" {
  description = "Service account identity allowed to promote curated files toward staging."
  value       = module.iam_bindings.data_loader_sa_email
}

output "analytics_viewer_service_account_email" {
  description = "Service account identity restricted to Row-Level Security protected reads."
  value       = module.iam_bindings.analytics_viewer_sa_email
}

output "cloud_sql_connection_name" {
  description = "Connection string of the private Cloud SQL PostgreSQL instance."
  value       = module.cloud_sql_staging.instance_connection_name
}

output "application_url" {
  description = "Public HTTPS entry point of the staging App Engine application."
  value       = module.app_engine_staging.application_url
}
