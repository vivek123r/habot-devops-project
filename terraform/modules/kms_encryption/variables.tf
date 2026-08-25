###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/kms_encryption/variables.tf
###############################################################################

variable "project_id" {
  description = "Google Cloud project identifier hosting the key ring."
  type        = string
}

variable "region" {
  description = "Region of the key ring; keys never leave their region."
  type        = string
}

variable "rotation_period_days" {
  description = "Rotation period applied to every key, in days."
  type        = number
}

variable "labels" {
  description = "Labels copied onto every key."
  type        = map(string)
}

variable "storage_service_agent" {
  description = "Email of the Cloud Storage service agent that encrypts bucket objects."
  type        = string
}

variable "bigquery_cmek_agent" {
  description = "Email of the BigQuery encryption service agent that encrypts datasets."
  type        = string
}

variable "pubsub_service_agent" {
  description = "Email of the Pub/Sub service agent that encrypts topic message data."
  type        = string
}
