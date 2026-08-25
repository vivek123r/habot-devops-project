###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/app_engine_staging/variables.tf
###############################################################################

variable "project_id" {
  description = "Google Cloud project identifier hosting the application."
  type        = string
}

variable "region" {
  description = "Primary region of the platform; the App Engine location is derived from it."
  type        = string
}

variable "name_prefix" {
  description = "Naming prefix used for derived identifiers."
  type        = string
}

variable "app_engine_location" {
  description = "App Engine location code. Derived from region by default; App Engine uses shorter location codes for some regions."
  type        = string
  default     = null
}
