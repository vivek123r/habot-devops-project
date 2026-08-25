# Data Flow, Logical, Security, and Pipeline Diagrams

**Candidate : Vivek R — vivekravi9496497657@gmail.com | +91 8590609366**

All four diagrams describe one system. Names match Terraform resources and backend modules
exactly.

## 1. Data Flow Diagram

### Mermaid

```mermaid
sequenceDiagram
    autonumber
    actor Parent
    participant API as App Engine<br/>Django Rest Framework
    participant DCYN as Decision Yes/No Library<br/>(twelve binary rules)
    participant DB as Cloud SQL<br/>PostgreSQL private
    participant RAW as D0 Raw Landing<br/>Cloud Storage bucket
    participant TOPIC as Pub/Sub Topic<br/>student-onboarding-events-staging
    participant DLQ as Dead-Letter Topic<br/>quarantine after five attempts
    participant SINK as BigQuery Subscription<br/>use-table-schema enforced
    participant BQ as D1 Staged Enforced Table<br/>REQUIRED-mode schema

    Parent->>API: POST JSON onboarding form
    API->>DCYN: evaluate payload (R01..R12)
    alt every rule returns YES
        API->>DB: persist submission + decision record
        API->>RAW: archive raw payload under incoming/
        API->>TOPIC: publish validated event (JSON)
        TOPIC->>SINK: deliver message
        SINK->>BQ: write row (schema re-enforced)
        API-->>Parent: 201 ACCEPTED with decision record
    else any rule returns NO
        API-->>Parent: 400 REJECTED with per-rule record and codes
        Note over API,BQ: nothing persisted, nothing published
    end
    opt delivery fails five times
        SINK-->>DLQ: quarantine message for triage and replay
    end
```

### ASCII

```text
                 VALID PATH (every rule = YES)
 ┌────────┐   JSON    ┌─────────────┐  evaluate  ┌──────────────────┐
 │ Parent │──────────▶│  Django DRF │───────────▶│ Decision Yes/No  │
 └────────┘           │  on App     │            │ R01..R12 → YES   │
                      │  Engine     │◀───────────│                  │
                      └──┬───┬───┬──┘   verdict  └──────────────────┘
              persist    │   │   │ archive        publish
                         ▼   │   ▼                    ▼
               ┌──────────┐  │ ┌──────────────┐  ┌────────────────────┐
               │Cloud SQL │  │ │ D0 Raw       │  │ Pub/Sub events     │
               │Postgres  │  │ │ Landing      │  │ topic (CMEK)       │
               │private   │  │ │ incoming/,   │  └─────────┬──────────┘
               └──────────┘  │ │ retention    │            │ deliver
                             ▼ ▼ lock         ▼            ▼
                     schema-enforced sink  ┌────────────────────┐
                     BigQuery subscription▶│ D1 Staged Enforced │
                                           │ REQUIRED table     │
                                           └────────────────────┘

                 REJECT PATH (any rule = NO)
                      response 400 REJECTED + per-rule record
                      (nothing persisted, nothing published)

                 QUARANTINE PATH (delivery failure x5)
                      Pub/Sub events topic ──▶ dead-letter topic ──▶ triage pull
```

## 2. Logical Architecture Diagram

### Mermaid

```mermaid
flowchart TB
    subgraph Edge["Intake layer"]
        FE[React parent browser application]
        AE[App Engine standard service<br/>sa-onboarding-api-staging]
    end
    subgraph Transactional
        SQL[(Cloud SQL PostgreSQL 16<br/>private IP, IAM logins)]
        CONN[Serverless VPC Access connector]
    end
    subgraph Analytics["Streaming analytics layer"]
        PS[[Pub/Sub events topic]]
        DLQ[[Dead-letter topic + triage subscription]]
        BQS[BigQuery subscription sink]
        ENF[Enforced REQUIRED-mode table]
        CL[Principal clearance allowlist]
        SEC[Row-Level Security authorized view]
        AN[Analytics viewer<br/>sa-analytics-viewer-staging]
        LD[Data loader<br/>sa-data-loader-staging]
    end
    subgraph Platform["Foundations"]
        KMS[Key ring: storage, bigquery, pubsub keys<br/>ninety-day rotation]
        IAM[iam_bindings module:<br/>conditional least-privilege grants]
    end
    FE -->|HTTPS| AE --> SQL
    AE -.-> CONN -.-> SQL
    AE -->|validated only| PS --> BQS --> ENF
    PS -->|five failed attempts| DLQ
    ENF --- SEC
    CL --- SEC
    AN -->|view-only SELECT| SEC
    LD -->|curated promotion| ENF
    KMS -.- PS & ENF & SQL & DLQ
    IAM -.- AE & LD & AN & BQS
```

### ASCII

```text
 React browser ──HTTPS──▶ App Engine (Django REST Framework)
                              │                │
                     private SQL path     validated events only
                              ▼                ▼
                        Cloud SQL ◀──connector── Pub/Sub topic ──▶ BigQuery sink
                        PostgreSQL                          │           │
                        (IAM logins)                   failures ×5        ▼
                                                            Dead-letter  D1 Staged Enforced
                                                              quarantine table (partitioned)
                                                                             │
                                             clearance allowlist ────────────┤
                                                                             ▼
                                              Row-Level Security view ◀── analytics viewer
                                                                            (view-only reader)

 Foundations: customer-managed keys encrypt GCS / BigQuery / Pub/Sub;
              iam_bindings scopes every identity to its narrowest surface.
```

## 3. Security Diagram

### Mermaid

```mermaid
flowchart LR
    subgraph IdentityBoundaries["Identity boundaries"]
        RT[runtime account<br/>publish topic, create under incoming/<br/>cloudsql client, log+metric writer]
        LD[data loader<br/>read under raw/ only,<br/>load into staged dataset, replay]
        AV[analytics viewer<br/>secure-view dataViewer ONLY<br/>plus job user]
        PA[Pub/Sub service agent<br/>dataset editor for sink,<br/>dead-letter publisher]
    end
    subgraph Controls["Preventive controls"]
        PAP[public access prevention ENFORCED]
        UBLA[uniform bucket-level access]
        RET[retention lock ninety days + versioning + soft delete]
        CMEK[customer-managed keys rotate ninety days]
        PRIV[no public database address; encrypted-only connections]
        COND[Identity-and-Access-Management conditions on object prefixes]
    end
    subgraph Detective["Detective and corrective controls"]
        GL[Gitleaks full-history secret scan]
        TR[Trivy vulnerability, misconfiguration, secret scan]
        DEC[persisted per-rule decision records]
        DRILL[pipeline drill asserts detectors fire]
    end
    RT --- COND --- PAP --- UBLA
    LD --- COND
    RET -.- PAP
    CMEK -.- RT & LD & AV & PA
    PRIV -.- RT
    GL & TR & DRILL -->|fail closed, quarantine| DEC
```

### ASCII

```text
 WHO                                    WHAT THEY MAY DO                       ENFORCED BY
 runtime account        publish to events topic; create objects under     resource-level binding
                        incoming/ ONLY; reach private SQL; write logs     + object-prefix condition
 data loader            read objects under raw/ ONLY; load into staged    condition + dataset scope
                        dataset; replay curated events onto the topic
 analytics viewer       SELECT through secure view ONLY (parent email     view-level binding alone
                        excluded from projection); run own jobs
 Pub/Sub agent          write sink rows into staged dataset; forward      dataset binding +
                        failed deliveries to dead-letter topic            dead-letter publisher

 STANDING CONTROLS: public-access-prevention ENFORCED, uniform bucket access,
                    retention lock + versioning + soft delete,
                    customer-managed keys rotating every ninety days,
                    private-address-only database with encrypted-only sessions.

 DETECTIVE LAYER: full-history secret scan, dependency and misconfiguration scan,
                  persisted decision records, detector-health drill on every run.
                  Any red result quarantines the build before promotion.
```

## 4. CI/CD Pipeline Diagram

### Mermaid

```mermaid
flowchart TD
    PUSH[Push or Pull Request] --> CHK[Checkout - token limited to contents read]
    CHK --> G3[Gate 3 Python formatting - Black check]
    CHK --> G4[Gate 4 Python linting - Ruff]
    CHK --> G5[Gate 5 Terraform canonical formatting check]
    G5 --> G6[Gate 6 Terraform validate against provider schemas]
    CHK --> G7[Gate 7 Gitleaks over full Git history - exit 1 on finding]
    CHK --> G8[Gate 8 Trivy vulnerabilities, misconfigurations, secrets]
    G3 --> G9[Gate 9 Deterministic validation test suite - eighty-six tests]
    G4 --> G9
    G9 --> G9B[Gate 9b Django deployment checks + migration drift check]
    CHK --> DR[Poka-Yoke drill - planted secret must be detected]
    G6 --> AT[Gate 10 Deployment readiness attestation]
    G7 --> AT
    G8 --> AT
    G9B --> AT
    DR --> AT
    AT --> PROMO[Eligible for staging promotion by delivery job]
    G3 & G4 & G5 & G6 & G7 & G8 & G9 & G9B & DR -. any failure .-> Q[Quarantine - evidence captured, merge blocked, no attestation]
```

### ASCII

```text
 checkout (contents: read token)
   ├── Gate 3 Black format check ─────────────┐
   ├── Gate 4 Ruff lint ──────────────┐       │
   ├── Gate 5 terraform fmt -check ──┐│       │
   │             └─▶ Gate 6 validate ┘│       ├─▶ Gate 9 tests ─▶ Gate 9b deploy checks ─┐
   ├── Gate 7 gitleaks (full history)│       │                                          │
   ├── Gate 8 trivy fs scanners ─────┴───────┴───────────────▶ Gate 10 ATTESTATION ◀──┘
   └── drill: planted secret MUST trip detector ──────────────▶        │
                                                                promotion eligibility
 ANY RED ANYWHERE ──▶ FAIL CLOSED ──▶ QUARANTINE (evidence kept, attestation never runs,
                                            branch protection keeps merge impossible)
```

## 5. Consistency Notes

- Component names in every diagram equal Terraform resource names (`d0-raw-landing`,
  `d1_staged_enforced_staging`, `student-onboarding-events-staging`) and the backend topic
  constant `ONBOARDING_EVENTS_TOPIC`.
- The pipeline diagram matches job order and `needs:` edges in `.github/workflows/ci.yml`
  exactly; the attestation job lists all nine upstream jobs in its `needs`.
- The security diagram's grant list mirrors `terraform/modules/iam_bindings/main.tf` line for
  line.
