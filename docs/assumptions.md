# Assumptions Register

**Candidate : Vivek R — vivekravi9496497657@gmail.com | +91 8590609366**

The hiring document states: *"translate vague specifications into secure, operational, and
mathematically clean cloud architectures"*. Where the document leaves a parameter open, this
submission documents the assumption here - never silently, never attributed to the document.
Each entry lists the replacement procedure so a HabotConnect reviewer can see exactly how the
assumption would be swapped for an authoritative rule.

| Identifier | Area | The hiring document says | This submission assumes | Replacement procedure |
| --- | --- | --- | --- | --- |
| A-01 | Project identifier | Not specified | Deployment input `project_id`, validated by regex; never hardcoded | Set at `terraform plan/apply` time or pipeline variables |
| A-02 | Region | Not specified | `asia-south1` default (platform context is India-facing); restricted allowlist of three App Engine-capable regions | Change `region` variable; all resources co-locate automatically |
| A-03 | Environment scope | "critical staging scenario" | Exactly one environment label `staging`; production reuses the blueprint in its own project | Add project; validation currently admits only staging by design |
| A-04 | State backend | Not specified | Remote Google Cloud Storage state per bootstrap instructions in `terraform/README.md` | One-time administrator bucket creation; documented commands |
| A-05 | Payload field set | "incoming JSON payload (representing a student onboarding form)" | Nine fields: parent full name, parent email, parent phone, child full name, child date of birth, learning difficulty category, optional support needs summary, two consent booleans - derived from platform context (parents, children with learning difficulties) | Edit `backend/onboarding/constants.py` once; serializer, Decision Yes/No library, model, BigQuery schema, and workbooks all quote it |
| A-06 | Exact validation limits | "exact field validation limits" (values not provided) | Name lengths 2-120, email ≤ 254, phone international pattern, summary 10-1000 when present, child age 2-18 completed years inclusive, category closed seven-value set, consent must be literal boolean true | Same single-file edit as A-05; boundary tests update alongside constants |
| A-07 | Age window rationale | Not specified | Two through eighteen completed years matches Learning Support Assistant matching for early-childhood and school-age children | Replace bounds in constants; arithmetic and tests unchanged |
| A-08 | Category taxonomy | "children with learning difficulties" | Seven-value closed set (Attention Deficit Hyperactivity Disorder, Autism Spectrum Disorder, Dyslexia, Dysgraphia, Dyscalculia, Speech and Language Impairment, Other Diagnosed Learning Difficulty) | Extend tuple in constants; BigQuery clustering accepts new values automatically; spreadsheet regenerates via script |
| A-09 | Row-Level Security policy specifics | "Apply ... Row-Level Security (RLS) policies" (policies not defined) | Principal clearance allowlist joined on session user inside an authorized view; parent contact email excluded from projection; Terraform provider lacks native row-access-policy resource, equivalent Data Definition Language recorded below | Insert clearance rows for real principals; if policy semantics differ, replace the view predicate; migrate to native policies when provider support lands |
| A-10 | DCYN expansion | "binary Yes/No logic library (DCYN library)" | Read as Decision Yes/No: twelve stable rules R01-R12, outcomes exactly YES or NO, decision records persisted for audit | Add or retire rules in `dcyn.py` + constants; matrices regenerate from the same source |
| A-11 | Secret values | None exist in repository | All credentials arrive via environment injection or workload identity federation; the drill fixture key is fabricated and was never valid | Configure federation in the organization; nothing in-repo changes |
| A-12 | Cloud SQL encryption tier | Not specified | Google-managed at-rest encryption initially; customer-managed upgrade requires one-time Cloud SQL service agent provisioning | Grant encrypter role to the agent, then set `disk_encryption_key` on the instance |

## Native Row-Level Security equivalent (A-09)

The declarative view implements this predicate:

```sql
CREATE ROW ACCESS POLICY analytics_by_clearance ON
  `PROJECT.d1_staged_enforced_staging.student_onboarding_events_enforced`
GRANT TO (`group:analytics-consumers@habotconnect.example`)
FILTER USING (
  learning_difficulty_category IN (
    SELECT cleared_category
    FROM `PROJECT.d1_staged_enforced_staging.rls_principal_clearance`
    WHERE LOWER(principal_email) = SESSION_USER()
  )
);
```

This statement is recorded for migration completeness; it is intentionally **not** executed by
Terraform because the provider offers no declarative resource for it, and non-declarative
provisioner SQL would break idempotent replanning.
