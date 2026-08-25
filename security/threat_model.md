# Threat Model — Secure Staging Blueprint

**Candidate : Vivek R — vivekravi9496497657@gmail.com | +91 8590609366**

Scope: the staging platform defined by this repository. Method: STRIDE per trust boundary,
with the hiring scenario's two incidents treated as historical threats TM-02 and TM-07.

## Trust boundaries

1. Parent browser → App Engine (public internet edge)
2. App Engine runtime → data plane (Pub/Sub, Cloud Storage, Cloud SQL)
3. Streaming layer → BigQuery (message delivery boundary)
4. Continuous integration → repository and cloud (supply-chain boundary)
5. Analytics consumers → curated data (row visibility boundary)

## Threat register

| Identifier | Boundary | STRIDE category | Threat scenario | Existing controls | Residual risk and treatment |
| --- | --- | --- | --- | --- | --- |
| TM-01 | 1 | Spoofing | Attacker floods the public form endpoint | Anonymous rate throttling (sixty per minute default), JSON envelope strictness, platform TLS | Distributed flooding is a platform-edge concern; enable Google Cloud Armor policy in production project |
| TM-02 | any | Information disclosure | **Hiring scenario:** raw application programming interface credentials committed to source | Gitleaks over full history at gate 7; Trivy secret scanner; pre-commit mirror; drill job proving detector health every run; redacted failure output; no allowlist outside quarantined fixtures | History rewriting after an actual leak is operational, not automatic; documented runbook step: rotate the exposed credential first, then purge |
| TM-03 | 2 | Elevation of privilege | Runtime identity attempts to read or overwrite foreign objects | Identity limited to object creation under `incoming/` by condition; no read role on its own bucket writes; uniform bucket access prevents ACL games | None material; conditions evaluated by the platform on every request |
| TM-04 | 2 | Tampering | Accepted payload mutated between validation and analytics | Event published only from persisted validated payload; sink re-enforces schema; dead-letter quarantine catches mismatches instead of writing them | Message ordering is best-effort by Pub/Sub design; consumers key rows by submission identifier |
| TM-05 | 3 | Denial of service | Sink outage stalls intake | Decoupled topics with seven-day retention and retained acknowledgements allow replay; retries with exponential backoff absorb transient outages | Prolonged outage fills dead-letter path deliberately rather than blocking acceptance |
| TM-06 | 4 | Tampering / Repudiation | Malicious or careless change reaches staging | Ten fail-closed gates, pinned tool versions, least-privilege workflow token (`contents: read`), required status checks block merge, quarantine evidence artifacts | Runner compromise is inherited platform risk; pin actions by commit SHA as next hardening step |
| TM-07 | 5 | Information disclosure | **Hiring scenario:** schema mismatch breaks downstream analytics; also over-broad analyst visibility | REQUIRED-mode enforced table + use-table-schema sink rejects mismatched writes; Row-Level Security view limits rows by clearance and omits parent email; clearance table itself is not reader-accessible | Clearance administration is manual-by-design (operations duty) |
| TM-08 | 2 | Repudiation | Dispute about what was accepted and why | Persisted per-rule Decision Yes/No record with every submission; deterministic evaluator reproduces verdicts for any historical evaluation date | Records are immutable via application behavior; add object-versioned export for long-term audit |
| TM-09 | all | Information disclosure | Ransomware-style mass deletion of landing data | Versioning plus retention lock plus soft-delete window; `force_destroy = false`; deletion protection on tables and database | Determined privileged actor remains a risk; production adds bucket lock retention beyond ninety days |
| TM-10 | 4 | Spoofing | Pipeline impersonated to deploy unattested code | Attestation is a required status check produced only inside the trusted workflow; delivery pathway consumes attestation state, not chat messages | Workload identity federation recommended for the delivery credentials (recorded assumption A-11) |

## Explicit non-goals

- Distributed denial-of-service absorption at edge scale (platform service territory).
- Field-level encryption of free-text summaries (requires product decision on search needs;
  noted for the security council).
