# Traceability Matrix — Hiring Document → Implementation → Evidence

**Candidate : Vivek R — vivekravi9496497657@gmail.com | +91 8590609366**

Every requirement in the hiring document (Habot 1.0, dated 28 July 2026) is mapped below.
Quotations are from the document; "Evidence" names the exact file(s) and the verification that
proves compliance. Assumption-driven items are marked **(A-nn)** and link to
[`assumptions.md`](assumptions.md) - they are never presented as document requirements.

## 1. The Three Tasks

| # | Requirement (document wording) | Implementation | Evidence |
| --- | --- | --- | --- |
| T1.1 | "Write a Terraform configuration (main.tf) to securely provision a Google Cloud Storage (GCS) raw landing bucket (D0 Raw Landing)" | `google_storage_bucket.raw_landing` named `{prefix}-d0-raw-landing` with public access prevention enforced, uniform bucket-level access, versioning, retention lock, soft delete, customer-managed key | `terraform/modules/storage_raw_landing/main.tf`; `terraform validate` exit 0; `terraform fmt -check` exit 0 |
| T1.2 | "...and a BigQuery dataset (D1 Staged/Enforced)" | Dataset `d1_staged_enforced_staging` with default customer-managed encryption, table expiration, deletion protection, REQUIRED-mode enforced table partitioned by date with mandatory partition filter | `terraform/modules/bigquery_staged/main.tf`; same validation evidence |
| T1.3 | "Apply strict IAM conditions" | Conditional bindings on object-name prefixes (`incoming/`, `raw/`) plus resource-level topic and view bindings; all grants in one auditable module | `terraform/modules/iam_bindings/main.tf` lines for `google_storage_bucket_iam_member.condition`; reviewer-readable single file |
| T1.4 | "...and Row-Level Security (RLS) policies" **(A-09)** | Authorized secure view filtering by clearance allowlist joined on session user; consumers hold view-only read rights; parent email excluded from projection; native-policy DDL recorded for migration | `terraform/modules/bigquery_staged/main.tf` view + `google_bigquery_table_iam_member`; `docs/assumptions.md` A-09 |
| T2.1 | "Design a YAML configuration (e.g., GitHub Actions) that executes automated linter checks and security scans" | Ten-gate workflow: Black, Ruff, terraform fmt/validate, Gitleaks full history, Trivy vuln+misconfig+secret, tests, Django deploy checks, drill, attestation | `.github/workflows/ci.yml` |
| T2.2 | "...must act as a strict Fail-Closed gate - it must immediately fail, halt, and quarantine the build" | Every gate wired via `needs:`; no `continue-on-error` anywhere; quarantine job captures evidence on failure and attestation never runs; branch protection procedure documented | `ci.yml` needs graph; quarantine_on_failure job; `docs/demo_guide.md` reproduction steps |
| T2.3 | "...if formatting errors or raw, hardcoded API secret keys are detected" | Black rejects formatting drift; Gitleaks detects planted Google-shaped key (drill proves detection every run); Trivy secret scanner active | `ci.yml` gates 3,7,8 and quarantine_drill job; fixture `demo/violations/*` |
| T3.1 | "Deconstruct an incoming JSON payload ... into a binary Yes/No logic library (DCYN library)" **(A-10)** | `evaluate_submission()` returns one YES/NO per rule R01-R12, total and deterministic, framework-free, JSON-serializable records | `backend/onboarding/dcyn.py`; 30+ library tests in `onboarding/tests/test_dcyn_library.py` |
| T3.2 | "Write a clean Django REST Framework model serializer class with exact field validation limits" **(A-05, A-06)** | Explicit serializer with min/max lengths, patterns, closed choice set, strict envelope and exact-type law, stable machine-readable error codes | `backend/onboarding/serializers.py`; constants quoted from `backend/onboarding/constants.py`; 40+ serializer tests |
| T3.3 | "to entirely eliminate human judgment" | Identical input always yields byte-identical decision records and error codes (asserted by test); acceptance requires all twelve YES | Determinism tests in both test files; persisted record compared on repeat submission |

## 2. Assessment Criteria ("You Will Be Assessed On")

| # | Criterion | Implementation | Evidence |
| --- | --- | --- | --- |
| A.1 | "provision GCP App Engine and databases securely and cleanly using Terraform" | App Engine standard application shell + dedicated runtime identity; private Cloud SQL PostgreSQL 16 with IAM logins, backups, deletion protection; VPC connector | `terraform/modules/app_engine_staging/`, `terraform/modules/cloud_sql_staging/` |
| A.2 | "Poka-Yoke ... automated linter, formatting, and security build gates that block non-compliant code from deploying" | Full gate chain with promotion only downstream of attestation | `.github/workflows/ci.yml`; `docs/data_flow.md` pipeline diagram |
| A.3 | "Ensuring transactional schemas align with Pub/Sub and BigQuery streaming sinks without data loss" | BigQuery subscription with `use_table_schema = true` re-enforces REQUIRED columns; backoff retries; dead-letter quarantine; raw archive enables replay | `terraform/modules/pubsub_pipeline/main.tf`; ADR-005 |
| A.4 | "strict role-based access controls (RBAC) and following Least Privilege principles" | One identity per duty; four smallest-purpose project roles total; everything else resource-scoped or conditioned | `terraform/modules/iam_bindings/main.tf`; security diagram |
| A.5 | "Meticulous documentation, zero reliance on placeholders, absolute adherence to structural rules" | This repository: every file headered with name/contact; assumptions register; traceability matrix; no placeholder tokens (verified by final sweep); workbooks Wrap-Text verified programmatically | Repository-wide; `data/scripts/generate_workbooks.py` self-check |

## 3. Submission Instructions

| # | Requirement | Implementation | Evidence |
| --- | --- | --- | --- |
| S.1 | "Deliver your completed Terraform, YAML, and Python code blocks in a structured folder layout" | Professional tree exactly as section 8 of README | Repository structure |
| S.2 | "Present the engineering logic behind your automated linter gates and data pipelines" | Architecture rationale + decisions + diagrams | `docs/architecture.md`, `docs/decisions.md`, `docs/data_flow.md` |
| S.3.a | "architectural overview and logic flow using a Google Slides or PowerPoint presentation (Maximum of 15 slides)" | Twelve-slide deck content ready to paste into Slides/PowerPoint | `presentation/slides.md`, `presentation/speaker_notes.md` |
| S.3.b | "Demonstrate how your automated build gate successfully triggers a Fail-Closed status on invalid or insecure commits" | Reproducible three-scenario demo with expected console output and screenshot checklist | `docs/demo_guide.md` |
| S.3.c | "All spreadsheet worksheets ... must have Wrap Text enabled ... Use Full Forms Only" | Both workbooks generated with wrap-text on every populated cell, asserted post-generation; full-form vocabulary throughout | `data/schema_mapping.xlsx`, `data/dcyn_logic_matrix.xlsx`, verification inside generator |
| S.3.d | "answer document and code files are clearly labeled with your full name and contact information at the top" | Candidate header block at the top of every code, workflow, policy, workbook script, and documentation file | Any file in repository (first lines) |
| S.4 | Submission via the stated Google Form link | Out-of-repo action for the candidate; package assembled here | README footer notes deadline 25 August 2026 |

## 4. Context Obligations

| # | Requirement | Implementation | Evidence |
| --- | --- | --- | --- |
| C.1 | Scenario: unencrypted credentials in code must be caught | Secret scanning over full history + drill proving detector health; remediation path documented | `security/threat_model.md` threat TM-02; demo guide scenario two |
| C.2 | Scenario: schema mismatch breaking analytics must be prevented | Double schema enforcement (serializer + sink), dead-letter quarantine, replayable raw archive | Task rows above; architecture rationale section 2 |
| C.3 | "You must know its Values / Leadership Principles" | Interview preparation notes include values-alignment talking points | `docs/interview_prep.md` |

## 5. Verification Status Snapshot

| Check | Command | Status at submission |
| --- | --- | --- |
| Python formatting | `black --check backend/ data/` | Pass (23 files unchanged) |
| Linting | `ruff check backend/ data/` | Pass |
| Terraform format | `terraform fmt -check -recursive` | Pass |
| Terraform validity | `terraform validate` | Pass (Google provider ~> 6.0 schemas) |
| Test suite | `python -m pytest onboarding/tests` | Pass (86 tests) |
| Deploy readiness | `manage.py check --deploy --fail-level WARNING` + `makemigrations --check` | Pass |
| Workbook Wrap Text | generator self-verification | Pass (both files, every populated cell) |
