###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : variables.tf
# Purpose   : Single source of truth for every external input. Each variable
#             carries an explicit validation block so malformed or unsafe
#             inputs are rejected at plan time (Poka-Yoke: make the wrong
#             state impossible to provision).
###############################################################################

variable "project_id" {
  description = "Google Cloud project identifier that receives the staging resources."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "The project_id value must be a valid Google Cloud project identifier: lowercase letters, digits, and hyphens, starting with a letter, between 6 and 30 characters in total."
  }
}

variable "project_number" {
  description = "Numeric identifier of the same project, required to derive Google-managed service agent identities for Customer-Managed Encryption Key grants."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{12}$", var.project_number))
    error_message = "The project_number value must be exactly 12 digits."
  }
}

variable "region" {
  description = "Single Google Cloud region hosting every regional resource so data never leaves its compliance boundary."
  type        = string
  default     = "asia-south1"

  validation {
    # App Engine standard environment availability constrains this set.
    condition     = contains(["asia-south1", "europe-west1", "us-central1"], var.region)
    error_message = "The region value must be one of: asia-south1, europe-west1, us-central1. Every resource is co-located in one region by design."
  }
}

variable "environment" {
  description = "Deployment stage label stamped onto resources and Identity and Access Management conditions."
  type        = string
  default     = "staging"

  validation {
    condition     = contains(["staging"], var.environment)
    error_message = "Only the staging environment is provisioned by this configuration; production follows the identical blueprint with its own project."
  }
}

variable "owner_label" {
  description = "Accountable engineer recorded on every resource label for audit trails."
  type        = string
  default     = "vivek-r"

  validation {
    condition     = can(regex("^[a-z0-9-]{2,63}$", var.owner_label))
    error_message = "The owner_label value must be lowercase letters, digits, and hyphens, between 2 and 63 characters."
  }
}

variable "cost_center_label" {
  description = "Cost center code applied as a label for billing attribution."
  type        = string
  default     = "cc-eng-staging"

  validation {
    condition     = can(regex("^[a-z0-9-]{2,63}$", var.cost_center_label))
    error_message = "The cost_center_label value must be lowercase letters, digits, and hyphens, between 2 and 63 characters."
  }
}

variable "raw_landing_retention_days" {
  description = "Minimum number of days objects in the raw landing bucket remain immutable under the retention policy."
  type        = number
  default     = 90

  validation {
    condition     = var.raw_landing_retention_days >= 90 && var.raw_landing_retention_days <= 365
    error_message = "The raw_landing_retention_days value must be between 90 and 365 days inclusive."
  }
}

variable "staged_table_expiration_days" {
  description = "Default lifetime of staged BigQuery tables that do not override it; prevents abandoned analytics debris from accumulating cost."
  type        = number
  default     = 180

  validation {
    condition     = var.staged_table_expiration_days >= 30 && var.staged_table_expiration_days <= 365
    error_message = "The staged_table_expiration_days value must be between 30 and 365 days inclusive."
  }
}

variable "pubsub_message_retention_days" {
  description = "Number of days Pub/Sub retains messages for replay after downstream incidents."
  type        = number
  default     = 7

  validation {
    condition     = var.pubsub_message_retention_days >= 1 && var.pubsub_message_retention_days <= 31
    error_message = "The pubsub_message_retention_days value must be between 1 and 31 days inclusive."
  }
}

variable "kms_rotation_period_days" {
  description = "Customer-Managed Encryption Key rotation period in days for all managed keys."
  type        = number
  default     = 90

  validation {
    condition     = var.kms_rotation_period_days >= 30 && var.kms_rotation_period_days <= 365
    error_message = "The kms_rotation_period_days value must be between 30 and 365 days inclusive."
  }
}
