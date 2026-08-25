# Terraform Staging Blueprint - Operating Notes

**Candidate : Vivek R - vivekravi9496497657@gmail.com | +91 8590609366**

## Layout

Root configuration wires eight focused modules. Each module owns exactly one concern and
carries its own `main.tf`, `variables.tf` (with validation), and `outputs.tf`.

| Module | Owns |
| --- | --- |
| `project_services` | Required Google Cloud APIs, disable-on-destroy protection |
| `kms_encryption` | Key ring + three rotating keys + service-agent grants |
| `storage_raw_landing` | D0 Raw Landing bucket (hardening in resource body) |
| `bigquery_staged` | D1 dataset, enforced table, clearance table, secure view |
| `pubsub_pipeline` | Events topic, dead-letter topic + triage, schema-enforced sink |
| `cloud_sql_staging` | Network, subnet, private services access, connector, PostgreSQL |
| `app_engine_staging` | Regional application shell + dedicated runtime identity |
| `iam_bindings` | Every Identity and Access Management grant, conditional where possible |

## Commands

```bash
terraform fmt -check -recursive     # canonical form gate
terraform init -backend=false       # resolve modules/providers without credentials
terraform validate                  # provider-schema validation gate
terraform plan -var project_id=... -var project_number=...
terraform apply ...
```

## Inputs

Every variable is validated at plan time; see `variables.tf`. The two required inputs are
`project_id` and its twelve-digit `project_number`. Defaults pin the blueprint to one region
(`asia-south1`) with a three-region allowlist chosen for App Engine standard availability.

## Remote state bootstrap (one-time, administrator)

Remote state storage cannot create itself, so the bucket is created outside Terraform, once.
Choose any globally unique name; the example shows our naming convention:

```bash
gcloud storage buckets create gs://PROJECT-IDENTIFIER-tfstate-staging \
  --location=REGION --uniform-bucket-level-access --public-access-prevention
gcloud storage buckets update gs://PROJECT-IDENTIFIER-tfstate-staging --versioning
```

Then add the backend block locally (kept out of version control by `.gitignore` pattern):

```hcl
terraform {
  backend "gcs" {
    bucket = "your-state-bucket-name"
    prefix = "habotconnect/staging"
  }
}
```

## Outputs

Run `terraform output` after apply for: bucket name and URL, dataset identifier and location,
enforced-table and secure-view identifiers, topic names, service account emails, Cloud SQL
connection string, and the application URL - everything the deployment guide and the backend
configuration consume.
