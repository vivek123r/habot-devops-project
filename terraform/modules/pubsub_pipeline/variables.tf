###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/pubsub_pipeline/variables.tf
###############################################################################

variable "project_id" {
  description = "Google Cloud project identifier hosting the pipeline."
  type        = string
}

variable "region" {
  description = "Region pinning the message storage policy."
  type        = string
}

variable "message_retention_days" {
  description = "Message retention window on the events topic, in days."
  type        = number
}

variable "labels" {
  description = "Labels copied onto every topic."
  type        = map(string)
}

variable "kms_key_id" {
  description = "Full identifier of the Customer-Managed Encryption Key protecting message data."
  type        = string
}

variable "enforced_table_id" {
  description = "Fully qualified BigQuery table receiving validated events."
  type        = string
}
