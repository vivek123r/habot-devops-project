###############################################################################
# Candidate : Vivek R
# Contact   : vivekravi9496497657@gmail.com | +91 8590609366
# Project   : HabotConnect Hiring Project 1.0
#             Junior Cloud & DevOps Engineer (GCP / Django / React)
# File      : main.tf
# Purpose   : Root wiring for the secure staging blueprint (Task 1). Composes
#             focused modules so every concern has exactly one owner:
#               project_services   - required Google Cloud APIs
#               kms_encryption     - Customer-Managed Encryption Keys + agent grants
#               storage_raw_landing- D0 Raw Landing bucket (write-once archive)
#               bigquery_staged    - D1 Staged/Enforced dataset + Row-Level Security view
#               pubsub_pipeline    - streaming ingestion with dead-letter quarantine
#               app_engine_staging - regional App Engine application shell + runtime identity
#               cloud_sql_staging  - private relational database for the Django backend
#               iam_bindings       - every grant in one auditable place (least privilege)
###############################################################################

locals {
  name_prefix = "${var.project_id}-staging"

  # Google-managed service agent identities that must receive encryption or
  # write permissions, derived per Google documentation:
  #   Cloud Storage agent      : service-PROJECT_NUMBER@gs-project-accounts.iam.gserviceaccount.com
  #   BigQuery encryption agent: service-PROJECT_NUMBER@bigquery-encryption.iam.gserviceaccount.com
  #   Pub/Sub agent            : service-PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com
  storage_service_agent = "service-${var.project_number}@gs-project-accounts.iam.gserviceaccount.com"
  bigquery_cmek_agent   = "service-${var.project_number}@bigquery-encryption.iam.gserviceaccount.com"
  pubsub_service_agent  = "service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

module "project_services" {
  source = "./modules/project_services"

  project_id = var.project_id
}

module "kms_encryption" {
  source = "./modules/kms_encryption"

  project_id            = var.project_id
  region                = var.region
  rotation_period_days  = var.kms_rotation_period_days
  labels                = local.default_labels
  storage_service_agent = local.storage_service_agent
  bigquery_cmek_agent   = local.bigquery_cmek_agent
  pubsub_service_agent  = local.pubsub_service_agent

  depends_on = [module.project_services]
}

module "storage_raw_landing" {
  source = "./modules/storage_raw_landing"

  project_id     = var.project_id
  region         = var.region
  name_prefix    = local.name_prefix
  retention_days = var.raw_landing_retention_days
  labels         = local.default_labels
  kms_key_id     = module.kms_encryption.storage_key_id

  depends_on = [module.kms_encryption]
}

module "bigquery_staged" {
  source = "./modules/bigquery_staged"

  project_id            = var.project_id
  region                = var.region
  dataset_id            = "d1_staged_enforced_staging"
  table_expiration_days = var.staged_table_expiration_days
  labels                = local.default_labels
  kms_key_id            = module.kms_encryption.bigquery_key_id

  depends_on = [module.kms_encryption]
}

module "pubsub_pipeline" {
  source = "./modules/pubsub_pipeline"

  project_id             = var.project_id
  region                 = var.region
  message_retention_days = var.pubsub_message_retention_days
  labels                 = local.default_labels
  kms_key_id             = module.kms_encryption.pubsub_key_id
  enforced_table_id      = module.bigquery_staged.enforced_table_id

  depends_on = [module.bigquery_staged]
}

module "cloud_sql_staging" {
  source = "./modules/cloud_sql_staging"

  project_id       = var.project_id
  region           = var.region
  name_prefix      = local.name_prefix
  runtime_sa_email = module.app_engine_staging.runtime_sa_email

  depends_on = [module.app_engine_staging]
}

module "app_engine_staging" {
  source = "./modules/app_engine_staging"

  project_id  = var.project_id
  region      = var.region
  name_prefix = local.name_prefix

  depends_on = [module.project_services]
}

module "iam_bindings" {
  source = "./modules/iam_bindings"

  project_id             = var.project_id
  raw_bucket_name        = module.storage_raw_landing.bucket_name
  dataset_id             = module.bigquery_staged.dataset_id
  secure_view_table_name = module.bigquery_staged.secure_view_table_name
  topic_name             = module.pubsub_pipeline.topic_name
  dlq_topic_name         = module.pubsub_pipeline.dlq_topic_name
  runtime_sa_email       = module.app_engine_staging.runtime_sa_email
  pubsub_service_agent   = local.pubsub_service_agent

  depends_on = [
    module.storage_raw_landing,
    module.bigquery_staged,
    module.pubsub_pipeline,
    module.app_engine_staging,
    module.cloud_sql_staging,
  ]
}
