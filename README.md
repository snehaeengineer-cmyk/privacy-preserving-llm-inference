# Privacy-Preserving LLM Inference via PII Masking

> **Can an automated Anonymization Proxy strip sensitive patient data from healthcare prompts — without destroying the clinical context an LLM needs to give a useful answer?**  
> This project implements a local anonymization proxy between healthcare applications and external LLM APIs (e.g., Groq API, public LLMs). The proxy detects direct identifiers and quasi-identifiers, resolves NER conflicts, masks PII with typed placeholders, enforces safety policies, validates LLM responses, and restores or generalizes outputs in real time.

---

## Authors

* **Raveena Kumari** — TH Köln, Communication Systems and Networks (`raveena_kumari.kumari@smail.th-koeln.de`)
* **Sneha Pillai** — TH Köln, Communication Systems and Networks (`sneha_dayanandan.pillai@smail.th-koeln.de`)

---

## The Problem

Healthcare applications increasingly leverage public LLM APIs for tasks like clinical documentation summarization, medical Q&A, referral notes, and lab result explanations. However, raw clinical prompts contain dense **Protected Health Information (PHI)** and **Personally Identifiable Information (PII)** — patient names, dates of birth, phone numbers, addresses, insurance IDs, and medical record numbers (MRNs) — which cannot legally cross a hospital's trusted perimeter under **GDPR** or **HIPAA**.

Simply redacting text destroys medical context. This project explores a smarter middle ground: **typed placeholder substitution and conflict-resolved entity masking**.

### Example Transformation

| Stage | Text |
|-------|------|
| **Raw input** | `Anna Müller, born 12.03.1980, lives in Munich and has Type 2 diabetes.` |
| **Masked prompt** | `[PATIENT_NAME_1], age group 40s, lives in [LOCATION_1] and has Type 2 diabetes.` |
| **LLM response** | `[PATIENT_NAME_1] should monitor blood glucose and attend regular check-ups.` |
| **Final output (Generic Mode)** | `The patient should monitor blood glucose and attend regular check-ups.` |

The diagnosis (`Type 2 diabetes`) and clinically relevant age band (`age group 40s`) are preserved, while direct identifiers are completely masked before crossing the trust boundary.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Trusted [" TRUSTED CLOUD PERIMETER (Local / Hospital Boundary)"]
        direction TB
        App["Healthcare App (EHR)"]
        Handler["Request Handler"]
        NER["PII & Biomedical Detection Engine"]
        Resolver["Conflict Resolver"]
        Masker["Masking Engine"]
        Vault["Mapping Vault (In-Memory)"]
        Policy["Policy Engine (PASS / WARN / BLOCK)"]
        Validator["Local Response Validator"]
        DeAnon["De-Anonymizer / Generic Replacer"]
        Audit["Metadata Audit Logger"]

        App -->|1. Raw Clinical Prompt| Handler
        Handler --> NER --> Resolver --> Masker
        Masker -->|Store Token Mappings| Vault
        Masker --> Policy
        Validator --> DeAnon
        DeAnon -->|2. De-masked or Generic Output| App
        Handler -.->|Log Metadata Only| Audit
    end

    subgraph Untrusted [" UNTRUSTED EXTERNAL ENVIRONMENT"]
        LLM["Public LLM API (Groq API / Mock Mode)"]
    end

    Policy ==>|3. Masked Prompt Only (HTTPS)| LLM
    LLM ==>|4. Tokenized Response| Validator

    style Trusted fill:#0d1117,stroke:#58a6ff,stroke-width:2px,color:#fff
    style Untrusted fill:#161b22,stroke:#f85149,stroke-width:2px,color:#fff
