# Poka-Yoke Demonstration Guide

**Candidate : Vivek R — vivekravi9496497657@gmail.com | +91 8590609366**

This guide reproduces the fail-closed demonstration required by submission instruction 3b.
Three scenarios, each fully reproducible, with expected console output and a screenshot
checklist for the interview deck.

## One-time preparation

1. Create an empty GitHub repository and push this project to its `main` branch:

```bash
git init
git add .
git commit -m "HabotConnect hiring project: secure staging blueprint"
git branch -M main
# Then follow the instructions GitHub displays for pushing an existing
# repository, adding your new repository as the remote named origin.
git push -u origin main
```

2. In the repository settings, open **Branches → Add branch protection rule** for `main`:
   - Require a pull request before merging.
   - Require status checks: select every job name from `ci.yml`, especially
     **Gate 10 - Deployment Readiness Attestation**.
   - Require branches to be up to date before merging.

   This is what turns "the pipeline failed" into "the commit is quarantined": merging becomes
   mechanically impossible until every gate is green again.

3. Confirm the first run of the workflow on `main` shows every gate green, including the
   **Poka-Yoke Drill** job. Screenshot this as the baseline (Deck slide 8).

## Scenario one — Valid commit passes all gates

```bash
git checkout -b demo/valid-change
echo "# documentation-only change" >> docs/architecture.md
git add docs/architecture.md
git commit -m "docs: clarify raw landing rationale"
git push -u origin demo/valid-change
```

Open the pull request. Every gate completes green; the attestation step prints:

```text
============================================================
 POKA-YOKE ATTESTATION: ALL GATES GREEN
 Commit : <sha>
 Ref    : refs/heads/demo/valid-change
 Every mandatory gate passed. This commit alone is
 eligible for promotion to staging by the delivery job,
 which runs only downstream of this attestation.
============================================================
```

(The `<sha>` above is filled automatically by GitHub Actions at run time.)

**Screenshots:** green pipeline overview; attestation step expanded.

## Scenario two — Malformed code fails closed

The drill fixture doubles as the violation source. Copy the malformed file into application
code on a demo branch:

```bash
git checkout -b demo/bad-formatting
cp demo/violations/bad_formatting_example.py backend/onboarding/_demo_violation.py
git add backend/onboarding/_demo_violation.py
git commit -m "feat: intentionally malformed module for gate demonstration"
git push -u origin demo/bad-formatting
```

Gate 3 (Black) fails immediately with output ending in:

```text
would reformat backend/onboarding/_demo_violation.py
1 file would be reformatted, 21 files would be left unchanged.
```

Because every downstream job declares `needs:`, they never start. The run ends red; the
**Quarantine - Capture Evidence On Failure** job prints the failed-need list; the pull request
shows merge blocked by the required checks.

Clean up: delete the branch locally and remotely after capturing screenshots.

A second malformed fixture, `demo/violations/insecure_terraform_example.tf`, exercises the
Terraform gates the same way: copying it under `terraform/` makes Gate 5
(`terraform fmt -check`) fail closed identically. It lives outside the configuration
directory so the main branch stays green while the fixture remains available.

## Scenario three — Leaked secret fails closed and quarantines

```bash
git checkout -b demo/leaked-secret
cp demo/violations/leaked_api_credentials.txt backend/settings_local.py
git add backend/settings_local.py
git commit -m "chore: intentionally planted secret for detector demonstration"
git push -u origin demo/leaked-secret
```

Gate 7 (Gitleaks) exits 1 with a finding like:

```text
Finding:     backend/settings_local.py:12
Secret:      AIzaSy****... (redacted)
RuleID:      gitleaks-rule-id-google-api-key
```

Note the value renders redacted because the gate passes `--redact`: even the failure output
refuses to echo the secret. The report artifact `gitleaks-report` is attached to the run for
triage; the attestation job never executes; the pull request cannot merge. The Trivy gate
would independently flag the same file through its own secret scanner - two detectors, one
conclusion.

**Screenshots:** failed Gate 7 step with redaction visible; quarantined run summary; blocked
merge banner on the pull request.

## Scenario four (live) — Data validation binary outcomes

With the local server running (`python manage.py runserver` from `backend/`):

```bash
# Accepted: 201 with all_rules_passed true
curl -s -X POST http://127.0.0.1:8000/api/v1/onboarding/submissions/ \
  -H "Content-Type: application/json" \
  --data-binary @../data/sample_payloads/valid_submission.json | python -m json.tool

# Rejected: 400 with ERR_REQUIRED_PARENTAL_CONSENT_GRANTED
curl -s -X POST http://127.0.0.1:8000/api/v1/onboarding/submissions/ \
  -H "Content-Type: application/json" \
  --data-binary @../data/sample_payloads/invalid_missing_parental_consent.json | python -m json.tool
```

Each response embeds the full per-rule Decision Yes/No record - the audience sees exactly
which binary rule produced the verdict. Repeat the same invalid request twice and show the
records are byte-identical: zero judgment, ever.

## Expected total wall-clock

Preparation five minutes once; each scenario under three minutes during the interview,
including screenshots.
