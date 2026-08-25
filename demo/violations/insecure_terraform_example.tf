###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Purpose   : Poka-Yoke drill fixture - deliberately insecure Terraform.
#             This file is NOT part of the real configuration; it exists so a
#             presenter can demonstrate that terraform fmt and review gates
#             reject sloppy infrastructure code.
###############################################################################

resource "google_storage_bucket" "bad_bucket" {
name = "${var.project_id}-insecure-demo"
location = "US"
force_destroy=true
uniform_bucket_level_access=false
public_access_prevention="inherited"
}
