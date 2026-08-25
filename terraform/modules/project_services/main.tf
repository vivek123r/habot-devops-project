###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/project_services/main.tf
# Purpose   : Enables exactly the Google Cloud APIs the staging blueprint
#             requires, with disable_on_destroy disabled so an accidental
#             destroy never removes shared tenancy capabilities from the
#             project. API enablement must complete before dependent modules.
###############################################################################

resource "google_project_service" "enabled" {
  for_each = toset([
    "cloudkms.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "pubsub.googleapis.com",
    "appengine.googleapis.com",
    "sqladmin.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
    "serviceusage.googleapis.com",
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}
