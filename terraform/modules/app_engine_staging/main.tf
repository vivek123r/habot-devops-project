###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/app_engine_staging/main.tf
# Purpose   : Regional App Engine application shell plus the dedicated runtime
#             service account the Django REST Framework service executes as.
#
#             Boundary decision: infrastructure-as-code provisions the
#             application and its identity; application versions are deployed
#             by the delivery pipeline only after every Poka-Yoke gate passes.
#             This keeps immutable-infrastructure concerns separated from
#             build-artifact promotion, and it means a failed gate can never
#             reach this environment - the fail-closed property demanded by
#             Task 2.
#
#             The default App Engine service account is never used: the
#             runtime identity below carries only the roles granted in
#             modules/iam_bindings.
###############################################################################

locals {
  # App Engine predates some modern region codes and expects short location
  # identifiers for the classic regions.
  app_engine_location_codes = {
    "asia-south1"  = "asia-south1"
    "europe-west1" = "europe-west"
    "us-central1"  = "us-central"
  }

  app_engine_location = coalesce(
    var.app_engine_location,
    local.app_engine_location_codes[var.region]
  )
}

resource "google_service_account" "runtime" {
  project      = var.project_id
  account_id   = "sa-onboarding-api-staging"
  display_name = "Onboarding Application Programming Interface Runtime (Staging)"
  description  = "Identity for the Django onboarding service on App Engine staging. Grants are managed exclusively in modules/iam_bindings."
}

resource "google_app_engine_application" "staging" {
  project     = var.project_id
  location_id = local.app_engine_location

  # The legacy default service account stays unused; every serving version is
  # deployed with the dedicated identity above.
  serving_status = "SERVING"

  feature_settings {
    split_health_checks = false
  }

  lifecycle {
    # The App Engine region is permanent per project; destroying and recreating
    # with a different location would strand the project.
    prevent_destroy = true
  }
}
