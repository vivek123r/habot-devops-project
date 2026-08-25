###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/kms_encryption/main.tf
# Purpose   : One regional key ring, three Customer-Managed Encryption Keys
#             (Cloud Storage, BigQuery, Pub/Sub), each rotated on a fixed
#             schedule and protected against destruction. Google-managed
#             service agents receive only the cryptoKeyEncrypterDecrypter
#             role on their own key - never admin - so encryption stays under
#             customer control while the platform can still write data.
#
#             Cloud SQL intentionally keeps its Google-managed default
#             encryption here; Customer-Managed Encryption for Cloud SQL
#             additionally depends on provisioning the project's Cloud SQL
#             service agent first, which is an organizational one-time step
#             recorded in docs/decisions.md with the exact upgrade path.
#
#             Note on rotation_period_seconds: the provider expresses the
#             rotation schedule in seconds; 90 days equals 7776000 seconds.
###############################################################################

resource "google_kms_key_ring" "staging" {
  project  = var.project_id
  name     = "habot-staging-key-ring"
  location = var.region
}

locals {
  rotation_period_seconds = var.rotation_period_days * 24 * 60 * 60

  keys = {
    storage  = {}
    bigquery = {}
    pubsub   = {}
  }
}

resource "google_kms_crypto_key" "keys" {
  for_each = local.keys

  name            = each.key
  key_ring        = google_kms_key_ring.staging.id
  rotation_period = "${local.rotation_period_seconds}s"

  labels = var.labels

  lifecycle {
    prevent_destroy = true
  }
}

# Each Google-managed service agent may encrypt and decrypt with exactly its
# own key. No project-wide Cloud Key Management Service permissions are issued.
resource "google_kms_crypto_key_iam_member" "storage_agent" {
  crypto_key_id = google_kms_crypto_key.keys["storage"].id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${var.storage_service_agent}"
}

resource "google_kms_crypto_key_iam_member" "bigquery_agent" {
  crypto_key_id = google_kms_crypto_key.keys["bigquery"].id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${var.bigquery_cmek_agent}"
}

resource "google_kms_crypto_key_iam_member" "pubsub_agent" {
  crypto_key_id = google_kms_crypto_key.keys["pubsub"].id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${var.pubsub_service_agent}"
}
