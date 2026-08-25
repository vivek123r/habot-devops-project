###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/storage_raw_landing/variables.tf
###############################################################################

variable "project_id" {
  description = "Google Cloud project identifier hosting the bucket."
  type        = string
}

variable "region" {
  description = "Region of the bucket, co-located with every other resource."
  type        = string
}

variable "name_prefix" {
  description = "Naming prefix derived from project and environment."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]{3,63}$", var.name_prefix))
    error_message = "The name_prefix value must be lowercase letters, digits, and hyphens between 3 and 63 characters so composed bucket names stay valid."
  }
}

variable "retention_days" {
  description = "Retention lock period applied to raw landing objects, in days."
  type        = number
}

variable "labels" {
  description = "Labels copied onto the bucket."
  type        = map(string)
}

variable "kms_key_id" {
  description = "Full identifier of the Customer-Managed Encryption Key protecting objects at rest."
  type        = string
}
