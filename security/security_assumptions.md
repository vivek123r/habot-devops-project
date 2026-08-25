# Security Assumptions and Posture Notes

**Candidate : Vivek R — vivekravi9496497657@gmail.com | +91 8590609366**

This file records the security-relevant decisions that are deliberately *not* enforced by code
in this repository, so a reviewer can distinguish implemented controls from organizational
prerequisites.

## Organizational prerequisites (assumed present)

1. **Workload identity federation** for the delivery pathway. The pipeline token is limited to
   `contents: read`; the credentials that eventually touch staging should be federated, never
   long-lived keys. Recorded as assumption A-11.
2. **Branch protection with required status checks**, including the attestation job. The
   workflow fails closed by itself; branch protection is what makes the quarantine
   administratively binding. Exact setup steps are in `docs/demo_guide.md`.
3. **State bucket administration.** Remote Terraform state lives in a versioned,
   access-controlled, encrypted bucket created once by an administrator; the procedure is in
   `terraform/README.md`.
4. **Cloud SQL service agent provisioning** precedes any customer-managed-key upgrade for the
   database; until then the instance uses Google-managed at-rest encryption (A-12).

## Secrets policy

- No credential exists anywhere in this repository. The one key-shaped string under
  `demo/violations/` is fabricated, labeled, allowlisted solely for the detector drill, and
  re-tested outside the allowlist on every pipeline run.
- Local development requires no secrets: `DJANGO_DEBUG=true` paths use no cloud dependencies
  and the event publisher defaults to a local null implementation.
- Staging injects values through App Engine environment composition at deploy time from
  protected pipeline state; nothing sensitive is committed or templated into version control.
- Failure outputs redact secret values (`--redact`) so even incident evidence does not leak.

## Data protection notes

- Parent contact email never appears in the Row-Level Security view projection; analytics
  cannot exfiltrate what it cannot select.
- Raw landing objects are retention-locked for at least ninety days, versioned, soft-delete
  protected, and encrypted with a rotating customer-managed key.
- Dead-letter messages inherit customer-managed encryption and remain inspectable for triage;
  silence is treated as data loss.

## Compensating-control honesty

Where this staging blueprint stops short of production hardening, it says so rather than
pretending: edge denial-of-service protection (Cloud Armor), action pinning by commit SHA,
long-term immutable audit export, and field-level encryption of free text are recorded as next
steps in the threat model's residual-risk column - each with its boundary and rationale.
