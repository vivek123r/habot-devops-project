###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : modules/project_services/outputs.tf
# Purpose   : Confirms completion so dependent modules can anchor on it.
###############################################################################

output "enabled_services" {
  description = "Set of Google Cloud APIs this module guarantees are enabled."
  value       = keys(google_project_service.enabled)
}
