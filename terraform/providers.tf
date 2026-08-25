###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : providers.tf
# Purpose   : Declares the Google Cloud provider and canonical default labels.
#             Credentials are never committed: they resolve from the executing
#             identity (CI Workload Identity Federation or operator
#             Application Default Credentials), so the pipeline fails closed if
#             no trustworthy identity exists rather than degrading silently.
###############################################################################

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  # Canonical labels applied to every labelable resource.
  # Values are lowercase, at most 63 characters, and match Google Cloud label rules.
  default_labels = {
    managed-by  = "terraform"
    project     = "habotconnect-hiring-project"
    component   = "secure-staging-data-platform"
    environment = var.environment
    data-domain = "student-onboarding"
    owner       = var.owner_label
    cost-center = var.cost_center_label
  }
}
