# Architecture

**Candidate : Vivek R — vivekravi9496497657@gmail.com | +91 8590609366**

## 1. Component Explanations

### 1.1 App Engine Standard (`terraform/modules/app_engine_staging`)
The Django Rest Framework onboarding service executes as a regional standard-environment
application under a dedicated service account. Infrastructure-as-code provisions the
application shell and its identity; application *versions* are promoted only by the delivery
pathway that sits downstream of the Poka-Yoke attestation job. This split is deliberate:
immutable infrastructure and mutable build artifacts have different risk profiles, different
approval paths, and different blast radii.

### 1.2 Cloud SQL PostgreSQL 16 (`terraform/modules/cloud_sql_staging`)
A private-address-only PostgreSQL instance backs the transactional side of the platform.
There is no public address to attack. Database logins use Cloud SQL Identity and Access
Management authentication, so no password materializes anywhere - not in Terraform state,
not in the pipeline, not in this repository. A Serverless VPC Access connector bridges the
standard environment to the private address space.

### 1.3 D0 Raw Landing bucket (`terraform/modules/storage_raw_landing`)
Every byte the intake produces is archived before anything else happens to it: versioned,
retention-locked for at least ninety days, public access prevention enforced, uniform bucket
access only, encrypted with a customer-managed key, soft-delete protected against ransomware
style deletion. The bucket is write-once by policy: the runtime identity can create objects
only under `incoming/`, and the loader identity can read them only under `raw/`.

### 1.4 Pub/Sub streaming spine (`terraform/modules/pubsub_pipeline`)
Validated events travel from the application to analytics through Pub/Sub. The BigQuery
subscription writes directly into the enforced table using the table's own schema, so a
message missing any required column is rejected by the sink itself. Delivery retries run an
exponential backoff from ten seconds to six hundred seconds with five attempts; exhausted
messages land in a dead-letter topic - quarantine, never silence. Topic retention preserves
message history for replay after downstream incidents.

### 1.5 D1 Staged/Enforced dataset (`terraform/modules/bigquery_staged`)
The enforced table mirrors the serializer contract column-for-column in REQUIRED mode,
partitioned by submission date with a mandatory partition filter and clustered by difficulty
category. The Row-Level Security surface is an authorized view whose predicate joins the base
table to a principal clearance allowlist on `SESSION_USER()`; consumers hold read rights on
the view alone, and parent email is excluded from its projection.

### 1.6 Customer-Managed Encryption (`terraform/modules/kms_encryption`)
One regional key ring holds one key per storage system, rotated every ninety days and
protected against destruction. Each Google-managed service agent receives
encrypter-decrypter on exactly its own key - nothing broader exists anywhere in the grant set.

### 1.7 Identity and Access Management (`terraform/modules/iam_bindings`)
Every permission lives in one auditable file. Project-wide roles are limited to
`cloudsql.client`, BigQuery job user, log writer, and metric writer - each already the
smallest role Google defines for its purpose. Everything else binds at resource level or
under Identity-and-Access-Management conditions on object-name prefixes.

### 1.8 Decision Yes/No validation core (`backend/onboarding/dcyn.py`)
Twelve rules, two outcomes. The library is framework-free so the identical evaluator runs in
request handling, in tests, and over archived payloads replayed from D0. Its decision records
persist beside accepted submissions, making every acceptance auditable against the exact
rules that were in force.

### 1.9 Poka-Yoke build gate (`.github/workflows/ci.yml`)
Ten sequential gates with pinned tool versions, a least-privilege workflow token, and no
`continue-on-error` anywhere. The final attestation job exists only downstream of all gates;
a quarantine job captures evidence when any gate fails. A drill job plants a known-bad secret
outside the training allowlist on every run and asserts the detector still fires.

## 2. Design Rationale

**Why archive raw payloads at all?** Because the scenario's schema mismatch broke analytics.
With immutable raw archives plus dead-letter quarantine, any downstream defect is replayable:
truth survives the bug.

**Why enforce the schema twice (serializer and BigQuery sink)?** Defense in depth across trust
boundaries. The serializer protects humans from typos; the sink protects analytics from every
other producer, including future services that never touch the serializer.

**Why an authorized view instead of a native row-access policy?** Terraform's Google provider
has no first-class resource for row-access-policy statements; encoding that DDL would require
non-declarative provisioner hacks that violate reproducibility. The authorized view achieves
identical row filtering with pure declarative resources. Assumption A-09 records the native
equivalent for migration.

**Why passwordless database logins?** Passwords leak through state files, pipelines, and
people. Identity-based logins make revocation instant (disable the service account) and make
credential rotation meaningless rather than merely scheduled.

## 3. Security Rationale Summary

| Control layer | Mechanism |
| --- | --- |
| Network | Private-only database, regional message-storage pinning, HTTPS termination by the platform |
| Identity | One dedicated account per duty; conditional prefix grants; zero wildcard project roles beyond four smallest-purpose roles |
| Data at rest | Customer-managed keys, ninety-day rotation, retention lock, soft delete |
| Data in flight | Platform TLS everywhere; JSON envelope strictness at the edge |
| Supply chain | Pinned tool versions, full-history secret scanning, dependency vulnerability scanning, branch protection requiring all gates |
| Auditability | Persisted per-rule decision records, quarantined failures with preserved reports |

## 4. Tradeoffs Considered

| Decision | Alternative rejected | Why |
| --- | --- | --- |
| Authorized view for RLS | Native row-access policy via provisioner | Provider lacks declarative resource; provisioner SQL breaks idempotence and drift detection |
| Cloud SQL Google-managed encryption | Customer-managed key immediately | Requires a one-time organizational service-agent provisioning step; upgrade path documented rather than half-wired |
| Dead-letter topic + pull triage | Dropping poison messages silently | Silent loss violates the "without data loss" criterion; quarantine keeps evidence |
| Explicit Serializer over ModelSerializer | ModelSerializer convenience | Input grammar must be owned explicitly; model defaults would leak storage concerns into the wire contract |
| Drill fixtures inside repository with narrow allowlist | No fixtures in repository | Keeping fixtures lets the pipeline prove detector health on every run instead of trusting an untested configuration |
| F2 instance class staging | F1 cheapest | Cold starts during interview demonstration cost more credibility than the price difference |

## 5. Consistency Statement

The Mermaid and ASCII diagrams in `docs/data_flow.md` describe the same components, names,
and flows defined by the Terraform modules above and consumed by the backend publisher;
`docs/traceability_matrix.md` maps each hiring-document requirement to these implementations
with file-level evidence.
