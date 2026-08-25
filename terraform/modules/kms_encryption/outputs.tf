###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/kms_encryption/outputs.tf
###############################################################################

output "storage_key_id" {
  description = "Full resource identifier of the Cloud Storage encryption key."
  value       = google_kms_crypto_key.keys["storage"].id
}

output "bigquery_key_id" {
  description = "Full resource identifier of the BigQuery encryption key."
  value       = google_kms_crypto_key.keys["bigquery"].id
}

output "pubsub_key_id" {
  description = "Full resource identifier of the Pub/Sub encryption key."
  value       = google_kms_crypto_key.keys["pubsub"].id
}
