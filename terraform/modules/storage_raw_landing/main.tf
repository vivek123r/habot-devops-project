###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/storage_raw_landing/main.tf
# Purpose   : The D0 Raw Landing bucket - the immutable entry point of every
#             byte entering the analytics platform.
#
#             Security controls applied:
#               - public_access_prevention = ENFORCED      (no public exposure, ever)
#               - uniform_bucket_level_access = true       (no per-object ACL drift)
#               - versioning + 90..365 day retention lock  (write-once evidence trail)
#               - Customer-Managed Encryption Key          (customer-held crypto)
#               - soft delete policy                       (ransomware recovery window)
#               - lifecycle rule aborting incomplete multipart uploads (cost hygiene)
#               - labels for audit and cost attribution
#
#             Identity and Access Management bindings intentionally live in
#             modules/iam_bindings so every grant is reviewable in one file.
###############################################################################

resource "google_storage_bucket" "raw_landing" {
  project = var.project_id

  name          = "${var.name_prefix}-d0-raw-landing"
  location      = var.region
  storage_class = "STANDARD"

  # Access hardening
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  # Immutability and recovery
  versioning {
    enabled = true
  }

  retention_policy {
    retention_period = var.retention_days * 24 * 60 * 60
  }

  soft_delete_policy {
    retention_duration_seconds = 30 * 24 * 60 * 60
  }

  # Cost hygiene: abandon half-finished uploads instead of billing them forever.
  lifecycle_rule {
    condition {
      age = 7
    }

    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }

  encryption {
    default_kms_key_name = var.kms_key_id
  }

  labels = var.labels

  force_destroy = false
}
