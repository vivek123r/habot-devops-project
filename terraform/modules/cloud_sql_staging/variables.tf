###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/cloud_sql_staging/variables.tf
###############################################################################

variable "project_id" {
  description = "Google Cloud project identifier hosting the database."
  type        = string
}

variable "region" {
  description = "Region of the instance, subnet, and connector."
  type        = string
}

variable "name_prefix" {
  description = "Naming prefix derived from project and environment."
  type        = string
}

variable "subnet_cidr" {
  description = "Private address block for the staging subnet."
  type        = string
  default     = "10.20.0.0/24"

  validation {
    condition     = can(cidrnetmask(var.subnet_cidr))
    error_message = "The subnet_cidr value must be a valid IPv4 Classless Inter-Domain Routing block."
  }
}

variable "connector_cidr" {
  description = "Dedicated /28 block for the Serverless VPC Access connector; must not overlap the subnet."
  type        = string
  default     = "10.20.1.0/28"

  validation {
    condition     = can(cidrnetmask(var.connector_cidr)) && split("/", var.connector_cidr)[1] == "28"
    error_message = "The connector_cidr value must be a valid IPv4 block with a /28 mask as required by Serverless VPC Access."
  }
}

variable "psa_prefix_length" {
  description = "Prefix length reserved for Private Services Access peering."
  type        = number
  default     = 16

  validation {
    condition     = var.psa_prefix_length >= 16 && var.psa_prefix_length <= 24
    error_message = "The psa_prefix_length value must be between 16 and 24."
  }
}

variable "runtime_sa_email" {
  description = "Email of the App Engine runtime service account that receives the passwordless database user."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+@[a-z0-9-]+\\.iam\\.gserviceaccount\\.com$", var.runtime_sa_email))
    error_message = "The runtime_sa_email value must be a valid Google service account email address."
  }
}
