###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/storage_raw_landing/outputs.tf
###############################################################################

output "bucket_name" {
  description = "Name of the D0 Raw Landing bucket."
  value       = google_storage_bucket.raw_landing.name
}

output "bucket_url" {
  description = "Uniform Resource Identifier of the D0 Raw Landing bucket."
  value       = google_storage_bucket.raw_landing.url
}
