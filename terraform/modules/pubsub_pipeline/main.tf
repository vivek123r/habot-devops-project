###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/pubsub_pipeline/main.tf
# Purpose   : Streaming ingestion spine connecting the validated Django REST
#             Framework payload to BigQuery without data loss.
#
#             Delivery guarantees:
#               - The BigQuery subscription writes directly into the
#                 enforced-schema table using use_table_schema, so a message
#                 missing any REQUIRED column is rejected by the sink itself.
#               - Exponential backoff retries (10 seconds to 600 seconds,
#                 maximum 5 delivery attempts) absorb transient sink outages.
#               - After exhausting attempts, messages land in the dead-letter
#                 topic - quarantine, not silence. A pull subscription keeps
#                 quarantined messages retrievable for triage and replay.
#               - Topic retention preserves acknowledged message history so
#                 downstream incidents can be replayed from source.
###############################################################################

resource "google_pubsub_topic" "events" {
  project = var.project_id

  name = "student-onboarding-events-staging"

  message_retention_duration = "${var.message_retention_days * 24 * 60 * 60}s"

  message_storage_policy {
    allowed_persistence_regions = [var.region]
  }

  kms_key_name = var.kms_key_id

  labels = var.labels
}

resource "google_pubsub_topic" "dlq" {
  project = var.project_id

  name = "student-onboarding-events-dlq-staging"

  message_retention_duration = "${max(var.message_retention_days, 7) * 24 * 60 * 60}s"

  message_storage_policy {
    allowed_persistence_regions = [var.region]
  }

  kms_key_name = var.kms_key_id

  labels = var.labels
}

resource "google_pubsub_subscription" "dlq_triage" {
  project = var.project_id

  name  = "student-onboarding-events-dlq-triage-staging"
  topic = google_pubsub_topic.dlq.id

  # Quarantined messages stay available for operators to inspect and replay.
  retain_acked_messages = true

  ack_deadline_seconds = 20

  expiration_policy {
    ttl = ""
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}

resource "google_pubsub_subscription" "events_to_bigquery" {
  project = var.project_id

  name  = "student-onboarding-events-to-bq-staging"
  topic = google_pubsub_topic.events.id

  # Keep the subscription alive even without active traffic in staging.
  expiration_policy {
    ttl = ""
  }

  ack_deadline_seconds = 60

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dlq.id
    max_delivery_attempts = 5
  }

  bigquery_config {
    table            = var.enforced_table_id
    use_table_schema = true
    write_metadata   = true
    # Unknown fields are never silently discarded: a mismatching payload is
    # rejected by the sink and quarantined via the dead-letter policy above.
  }

  depends_on = [google_pubsub_topic.dlq]
}
