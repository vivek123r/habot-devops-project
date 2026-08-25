###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/iam_bindings/variables.tf
###############################################################################

variable "project_id" {
  description = "Google Cloud project identifier for every binding."
  type        = string
}

variable "raw_bucket_name" {
  description = "Name of the D0 Raw Landing bucket used in condition expressions."
  type        = string
}

variable "dataset_id" {
  description = "Identifier of the D1 Staged/Enforced dataset."
  type        = string
}

variable "secure_view_table_name" {
  description = "Plain table identifier of the Row-Level Security protected view."
  type        = string
}

variable "topic_name" {
  description = "Name of the events topic."
  type        = string
}

variable "dlq_topic_name" {
  description = "Name of the dead-letter quarantine topic."
  type        = string
}

variable "runtime_sa_email" {
  description = "Email of the App Engine runtime service account."
  type        = string
}

variable "pubsub_service_agent" {
  description = "Email of the Google-managed Pub/Sub service agent."
  type        = string
}
