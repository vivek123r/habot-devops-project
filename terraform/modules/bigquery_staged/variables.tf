###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/bigquery_staged/variables.tf
###############################################################################

variable "project_id" {
  description = "Google Cloud project identifier hosting the dataset."
  type        = string
}

variable "region" {
  description = "Location of the dataset, co-located with every other resource."
  type        = string
}

variable "dataset_id" {
  description = "Identifier of the staged dataset."
  type        = string

  validation {
    condition     = can(regex("^[a-zA-Z0-9_]+$", var.dataset_id))
    error_message = "The dataset_id value may contain only letters, digits, and underscores."
  }
}

variable "table_expiration_days" {
  description = "Default table lifetime inside the dataset, in days."
  type        = number
}

variable "labels" {
  description = "Labels copied onto the dataset."
  type        = map(string)
}

variable "kms_key_id" {
  description = "Full identifier of the Customer-Managed Encryption Key protecting dataset storage."
  type        = string
}
