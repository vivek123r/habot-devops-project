###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/iam_bindings/main.tf
# Purpose   : Every permission in the staging blueprint lives here so an
#             auditor can review the entire authorization surface in one file.
#
#             Principals and their exact reach:
#
#               sa-onboarding-api-staging  (runtime, from App Engine module)
#                 - publish ONLY to the events topic (topic-level binding)
#                 - create objects ONLY under incoming/ of the D0 bucket
#                   (Identity and Access Management condition on object name)
#                 - connect to the private PostgreSQL instance (Cloud SQL client)
#                 - write platform logs and metrics
#
#               sa-data-loader-staging     (curated promotion pipeline)
#                 - view objects ONLY under raw/ of the D0 bucket (condition)
#                 - run BigQuery jobs and load INTO the D1 dataset
#                 - replay validated events onto the events topic
#
#               sa-analytics-viewer-staging (analytics consumers)
#                 - SELECT through the Row-Level Security view ONLY
#                   (binding attaches to the view table itself)
#                 - run their own BigQuery jobs
#                 - never touches the base table or the clearance allowlist
#
#               Pub/Sub service agent
#                 - write delivered events into the D1 dataset (sink contract)
#                 - forward failed deliveries to the dead-letter topic
#
#             Project-wide roles are limited to cloudsql.client, jobUser,
#             logging.logWriter, and monitoring.metricWriter - each already the
#             smallest role Google defines for its purpose. Everything else is
#             bound at the resource level.
###############################################################################

# ---------------------------------------------------------------------------
# Service accounts (except the runtime account, owned by the App Engine module)
# ---------------------------------------------------------------------------

resource "google_service_account" "data_loader" {
  project      = var.project_id
  account_id   = "sa-data-loader-staging"
  display_name = "Data Loader (Staging)"
  description  = "Promotes curated raw landing archives toward the staged dataset."
}

resource "google_service_account" "analytics_viewer" {
  project      = var.project_id
  account_id   = "sa-analytics-viewer-staging"
  display_name = "Analytics Viewer Row-Level Security (Staging)"
  description  = "Reads onboarding analytics exclusively through the Row-Level Security protected view."
}

# ---------------------------------------------------------------------------
# Runtime service account: publishing, raw archiving, database, observability
# ---------------------------------------------------------------------------

resource "google_pubsub_topic_iam_member" "runtime_publishes_events" {
  project = var.project_id
  topic   = var.topic_name
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${var.runtime_sa_email}"
}

resource "google_storage_bucket_iam_member" "runtime_writes_incoming" {
  bucket = var.raw_bucket_name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.runtime_sa_email}"

  condition {
    title       = "raw_landing_incoming_prefix_only_staging"
    description = "Runtime may create objects only under the incoming/ prefix of the raw landing bucket."
    expression  = "resource.name.startsWith(\"projects/_/buckets/${var.raw_bucket_name}/objects/incoming/\")"
  }
}

resource "google_project_iam_member" "runtime_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${var.runtime_sa_email}"
}

resource "google_project_iam_member" "runtime_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${var.runtime_sa_email}"
}

resource "google_project_iam_member" "runtime_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${var.runtime_sa_email}"
}

# ---------------------------------------------------------------------------
# Pub/Sub service agent: BigQuery sink delivery and dead-letter forwarding
# ---------------------------------------------------------------------------

resource "google_bigquery_dataset_iam_member" "pubsub_sink_writer" {
  project    = var.project_id
  dataset_id = var.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.pubsub_service_agent}"
}

resource "google_pubsub_topic_iam_member" "pubsub_forwards_dlq" {
  project = var.project_id
  topic   = var.dlq_topic_name
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${var.pubsub_service_agent}"
}

# ---------------------------------------------------------------------------
# Data loader: conditioned raw reads, staged writes, event replay
# ---------------------------------------------------------------------------

resource "google_storage_bucket_iam_member" "loader_reads_raw" {
  bucket = var.raw_bucket_name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.data_loader.email}"

  condition {
    title       = "raw_landing_raw_prefix_read_only_staging"
    description = "Loader may read objects only under the raw/ prefix of the raw landing bucket."
    expression  = "resource.name.startsWith(\"projects/_/buckets/${var.raw_bucket_name}/objects/raw/\")"
  }
}

resource "google_bigquery_dataset_iam_member" "loader_loads_staged" {
  project    = var.project_id
  dataset_id = var.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.data_loader.email}"
}

resource "google_project_iam_member" "loader_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.data_loader.email}"
}

resource "google_pubsub_topic_iam_member" "loader_replays_events" {
  project = var.project_id
  topic   = var.topic_name
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.data_loader.email}"
}

# ---------------------------------------------------------------------------
# Analytics viewer: Row-Level Security view exclusively
# ---------------------------------------------------------------------------

resource "google_bigquery_table_iam_member" "viewer_reads_secure_view_only" {
  project    = var.project_id
  dataset_id = var.dataset_id
  table_id   = var.secure_view_table_name
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.analytics_viewer.email}"
}
