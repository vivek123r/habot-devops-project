###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/pubsub_pipeline/outputs.tf
###############################################################################

output "topic_name" {
  description = "Name of the events topic."
  value       = google_pubsub_topic.events.name
}

output "dlq_topic_name" {
  description = "Name of the dead-letter quarantine topic."
  value       = google_pubsub_topic.dlq.name
}

output "bigquery_subscription_name" {
  description = "Name of the subscription writing into the enforced table."
  value       = google_pubsub_subscription.events_to_bigquery.name
}
