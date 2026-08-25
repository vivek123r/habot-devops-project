# Interview Preparation Notes

**Candidate : Vivek R — vivekravi9496497657@gmail.com | +91 8590609366**

Prepared as the hiring reviewer would probe: architecture, security, Terraform, pipeline,
Django, documentation, and culture. Each question includes the answer skeleton I can defend
from the repository.

## Technical questions most likely to be asked

1. **Why an authorized view instead of BigQuery row-access policies?**
   The Terraform Google provider has no first-class resource for row-access-policy statements;
   a provisioner-executed DDL hack breaks idempotence and drift detection. The view gives
   identical row filtering declaratively today; the native DDL is preserved in assumptions
   A-09 for migration.

2. **How does the design prevent another schema-mismatch incident?**
   Three layers: serializer at the edge; sink re-enforcement via `use_table_schema` so ANY
   producer missing REQUIRED columns is rejected; dead-letter quarantine plus replayable raw
   archive so nothing is silently lost or silently wrong.

3. **What exactly fails closed in the pipeline?**
   Every gate runs with pinned versions under a contents-read token, chained by `needs`. Any
   red result: downstream jobs never start, attestation never prints, quarantine job captures
   evidence, required status checks keep merge impossible. There is no continue-on-error line
   in the file.

4. **How do you know your secret detector actually works?**
   The drill job plants the fixture outside its allowlist every run and asserts Gitleaks exits
   1 and Black rejects the malformed file. Detector health is tested continuously, not assumed.

5. **Why customer-managed keys for some systems but not Cloud SQL?**
   Cloud SQL CMEK requires a one-time project service-agent provisioning step that belongs to
   organization setup; rather than half-wire it, the instance uses Google-managed encryption
   (still encrypted at rest) with the upgrade path recorded as assumption A-12.

6. **Where does the Django signing key live?**
   Never in the repository. Staging composes environment values from protected pipeline state
   at deploy time; local development needs none; tests use a throwaway value injected before
   settings import. Boot without a real key is refused whenever DEBUG is off.

7. **What stops someone adding `is_admin=true` to the payload?**
   Envelope strictness: unknown fields are rejected with a dedicated code before any coercion.
   The test suite proves it, and the DCYN record shows rule R11 as NO.

8. **Explain the age boundary arithmetic.**
   Completed years between birth date and evaluation date; inclusive window two through
   eighteen. Tests pin both edges from both sides: exactly-two accepted, one-day-short
   rejected, exactly-eighteen accepted, nineteen rejected — deterministic for any evaluation
   date because the date is injectable.

9. **Why Pub/Sub instead of writing straight to BigQuery?**
   Buffering decouples intake availability from sink availability; retention enables replay;
   the same topic feeds future consumers; dead-lettering turns poison into evidence.

10. **Least privilege — what is your smallest grant and your broadest?**
    Smallest: analytics viewer holds dataViewer on ONE view table only. Broadest:
    four project-level roles, each already the narrowest Google defines for its purpose
    (Cloud SQL client, BigQuery job user, log writer, metric writer).

11. **What happens if two submissions arrive simultaneously?**
    Both validated independently; persistence uses UUID primary keys; events publish per
    submission; no shared mutable state exists in the request path.

12. **If HabotConnect changes a validation limit next week, what touches?**
    One constants file plus regeneration of the spreadsheets and a test update; the build then
    enforces the new limit everywhere at once.

## Values and leadership-principles alignment

The document links two culture artifacts (Leadership Principles, Values PDFs) and names the
culture "highly accountable, detail-obsessed, Quiet Management". Talking points:

- **Accountability**: persisted decision records mean my system's verdicts carry their own
  evidence; I sign every file in this repository.
- **Detail obsession**: wrap-text verified programmatically; boundary tests on both sides of
  every limit; redacted even in failure output.
- **Quiet management**: gates hold the standard continuously so nobody needs to chase anyone;
  that is precisely how I prefer to work and to be evaluated.

## Questions I will ask the panel

1. Which staging signals matter most to the team in the first ninety days?
2. How do Learning Support Assistant matching rules evolve — who owns category taxonomy changes?
3. What is the promotion path from staging to production for data-platform changes?
