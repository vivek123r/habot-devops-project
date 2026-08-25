# Architecture Decision Records

**Candidate : Vivek R — vivekravi9496497657@gmail.com | +91 8590609366**

Format: context, decision, consequences. Each record is a commitment a reviewer can audit.

---

## ADR-001 — Centralize every validation limit in one constants module

**Context.** The scenario's root cause was schema drift between layers. A serializer with
inline limits, a hand-written BigQuery schema, and spreadsheets maintained by memory will
drift again.

**Decision.** `backend/onboarding/constants.py` is the single source of truth for field
names, bounds, patterns, category values, rule identifiers, and outcomes. The serializer
imports it; the Decision Yes/No library imports it; the model column sizes import it; the
BigQuery enforced table quotes the same values; the workbook generator imports it directly
from Python rather than retyping numbers into cells.

**Consequences.** Changing a limit is one edit plus regeneration of the workbooks; drift
between layers becomes structurally impossible rather than merely discouraged.

---

## ADR-002 — Remote Terraform state bootstrapped outside Terraform

**Context.** State storage cannot create itself without circularity.

**Decision.** Local state works out of the box; remote state bootstrap (versioned bucket,
public access prevention, encryption) is documented as an administrator one-time procedure in
`terraform/README.md`, with exact commands and naming convention.

**Consequences.** No placeholder backend block ships in version control; the bootstrap path is
explicit and auditable instead of implicit.

---

## ADR-003 — Authorized view implements Row-Level Security declaratively

**Context.** The hiring document requires RLS policies on the staged dataset, but the Google
provider for Terraform has no first-class resource for row-access-policy statements.

**Decision.** An authorized view (`student_onboarding_events_secure_view`) filters base rows
by joining the principal clearance allowlist against `SESSION_USER()`. Consumers receive
read rights on the view only - never the dataset - and parent email never appears in the view
projection. The equivalent native statement is preserved in `docs/assumptions.md`.

**Consequences.** Fully idempotent infrastructure-as-code today; documented migration path to
native policies when provider support arrives. Residual risk: clearance rows are managed by
platform operations rather than application code, which is intended separation.

---

## ADR-004 — Passwordless Cloud SQL via Identity and Access Management authentication

**Context.** Database passwords leak through state files, pipeline variables, and people.

**Decision.** The instance enables `cloudsql.iam_authentication`; the runtime service account
receives a `CLOUD_IAM_SERVICE_ACCOUNT` database user. No password exists anywhere.

**Consequences.** Revocation equals disabling one identity; rotation becomes meaningless.
Residual risk: token acquisition code must exist at deploy time (standard client libraries
handle it); documented in the deployment guide.

---

## ADR-005 — Dead-letter quarantine instead of silent drop or infinite retry

**Context.** "Without data loss" is explicit in the assessment criteria.

**Decision.** BigQuery subscription retries with ten-second-to-six-hundred-second backoff,
five attempts maximum, then forwards to a customer-managed-key-encrypted dead-letter topic
with its own triage pull subscription and retained acknowledged messages on the main topic.

**Consequences.** Poison messages are visible, inspectable, and replayable; analytics never
silently diverges from intake truth.

---

## ADR-006 — Quarantined training fixtures inside the repository, with a detector-health drill

**Context.** Demonstrating fail-closed behavior requires a real leaked-secret fixture; but any
fixture inside the scan scope would break the main branch build.

**Decision.** Fixtures live under `demo/violations/` behind exactly one allowlist entry in
`security/gitleaks.toml`. On every pipeline run, the drill job copies the fixture outside the
allowlisted path, asserts Gitleaks exits 1, and asserts Black rejects the malformed file.

**Consequences.** The demonstration is always available AND the detectors prove their own
health continuously; the allowlist cannot silently become a blind spot because the drill
would turn red.

---

## ADR-007 — Infrastructure provisions identity and shell; delivery promotes versions

**Context.** Mixing `terraform apply` with artifact deployment couples two different change
rhythms and weakens the meaning of both gates.

**Decision.** Terraform owns APIs, keys, buckets, datasets, topics, database, App Engine
application, and identities. Application versions deploy via `gcloud app deploy` only after
the attestation gate; the composed deployment descriptor gains connector and ephemeral key
values from protected pipeline state at deploy time.

**Consequences.** A failed Poka-Yoke gate can never reach staging by construction; infra and
app each roll back independently.

---

## ADR-008 — Explicit Serializer over ModelSerializer for the wire contract

**Context.** Untrusted external input deserves an explicitly owned grammar.

**Decision.** `StudentOnboardingSubmissionSerializer` declares fields, bounds, error codes,
and strict envelope/type law itself; persistence uses the model only after validation and the
Decision Yes/No record both succeed.

**Consequences.** Storage concerns cannot leak onto the wire contract; unknown-field and
exact-type rules are enforceable deterministically.
