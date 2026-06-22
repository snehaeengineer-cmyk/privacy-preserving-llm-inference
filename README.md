# System X: Privacy-Preserving LLM Inference via PII Masking

> **Can an automated Anonymization Proxy strip sensitive patient data from healthcare prompts — without destroying the clinical context an LLM needs to give a useful answer?**  
> This project builds a proxy layer between healthcare applications and public LLM APIs (e.g. GPT, Claude) that detects, masks, and later restores Personally Identifiable Information (PII) in real time.

> ⚠️ **Status: Implementation in Progress** — This README reflects the system design and planned evaluation. Code is actively being developed.

---

## 👥 Authors

Sneha Pillai, Mohamed Aziz Gam, Adrian Kramer, Raveena Kumari — TH Köln, Communication Systems and Networks

---

## 🧠 The Problem

Healthcare applications increasingly use public LLM APIs for tasks like clinical documentation, medical Q&A, and discharge summaries. But raw clinical prompts contain dense **Protected Health Information (PHI)** — patient names, dates of birth, addresses, insurance IDs — which cannot legally leave a hospital's trusted perimeter under **GDPR** or **HIPAA**.

Simply redacting text destroys medical context. This project explores a smarter middle ground: **typed placeholder substitution**.

**Example:**

| Stage | Text |
|-------|------|
| Raw input | `Anna Müller, born 12.03.1980, lives in Munich and has Type 2 diabetes.` |
| Masked prompt | `[PATIENT_NAME_1], born on [DATE_OF_BIRTH_1], lives in [LOCATION_1] and has Type 2 diabetes.` |
| LLM response | `[PATIENT_NAME_1] should monitor blood glucose and attend regular check-ups.` |
| Final output (Generic Mode) | `The patient should monitor blood glucose and attend regular check-ups.` |

The diagnosis (`Type 2 diabetes`) is preserved. The identity is not.

---

## ```mermaid
flowchart TD
    %% Define the Trusted Perimeter Box
    subgraph Trusted [🛡️ TRUSTED PERIMETER]
        direction TB
        App["📱 Healthcare App"]
        Proxy["🔒 Anonymization Proxy"]
        Vault["🗄️ Mapping Vault <br> (In-Memory)"]
        Validator["⚙️ Local Response Validator"]
        DeAnon["🔓 De-Anonymizer"]
        Output["🏁 Final Output"]

        %% Inner trusted flow
        App -->|Raw PII Data| Proxy
        Proxy -->|Store Tokens| Vault
        Validator --> DeAnon
        DeAnon --> Output
        Output -.->|Return to User| App
    end

    %% Define the Untrusted Box
    subgraph Untrusted [⚠️ UNTRUSTED ZONE]
        LLM["🤖 Public LLM API"]
    end

    %% Cross-boundary communication
    Proxy ====>|Masked Prompt Only <br> HTTPS| LLM
    LLM ====>|Inference Response| Validator

    %% Styling
    style Trusted fill:#0d1117,stroke:#58a6ff,stroke-width:2px,color:#fff
    style Untrusted fill:#161b22,stroke:#f85149,stroke-width:2px,color:#fff
```


**No raw PII ever crosses the trust boundary.**

---

## ```mermaid
flowchart TD
    %% Define Pipeline Steps
    Raw(["📄 Raw Clinical Prompt"])
    NER["1. NER Pipeline <br> <font size=2><i>Hybrid: Microsoft Presidio + spaCy + SciSpaCy (BC5CDR)</i></font>"]
    Mask["2. Masking Engine <br> <font size=2><i>Replace PII spans with placeholders (e.g., [PATIENT_NAME_1])</i></font>"]
    Vault["3. Mapping Vault <br> <font size=2><i>Volatile in-memory registry (never written to disk)</i></font>"]
    Policy["4. Policy Engine <br> <font size=2><i>Block if unsafe; pass if clean</i></font>"]
    Builder["5. Prompt Builder <br> <font size=2><i>Add placeholder-handling instructions for LLM</i></font>"]
    LLM[["🤖 6. Public LLM API <br> <font size=2><i>Receives ONLY the masked prompt</i></font>"]]
    Validator["7. Local Response Validator <br> <font size=2><i>Check placeholder integrity, PII leakage, hallucinations</i></font>"]
    DeMask["8. De-Masking Engine <br> <font size=2><i>Restore Mode OR Generic Mode</i></font>"]
    Output(["🏁 Final Output"])

    %% Sequential Data Flow
    Raw --> NER
    NER --> Mask
    Mask --> Vault
    Vault --> Policy
    Policy --> Builder
    Builder --> LLM
    LLM --> Validator
    Validator --> DeMask
    DeMask --> Output

    %% Custom Step Highlights
    style NER fill:#1f2937,stroke:#38bdf8,stroke-width:1px
    style Vault fill:#1f2937,stroke:#fbbf24,stroke-width:1px
    style LLM fill:#111827,stroke:#ef4444,stroke-width:2px
    style Validator fill:#1f2937,stroke:#34d399,stroke-width:1px
```


---

## 🔍 PII Categories Detected

| PII Category | Example | Detection Method | Placeholder |
|---|---|---|---|
| Patient Name | Anna Müller | Presidio + spaCy NER | `[PATIENT_NAME_1]` |
| Doctor Name | Dr. med. Schmidt | Presidio + spaCy NER | `[DOCTOR_NAME_1]` |
| Date of Birth | 12.03.1980 | Regex / Presidio | `[DATE_OF_BIRTH_1]` |
| Location | Munich | Presidio + spaCy NER | `[LOCATION_1]` |
| Hospital / Clinic | Klinikum rechts der Isar | Presidio + spaCy NER | `[ORGANIZATION_1]` |
| Email | anna@example.com | Presidio + Regex | `[EMAIL_1]` |
| Phone Number | +49 176 12345678 | Custom Regex / Presidio | `[PHONE_1]` |
| Insurance ID | A123456789 | Alpha-Numeric Regex | `[INSURANCE_ID_1]` |
| Medical Record No. | MRN-883921 | Hospital Pattern Regex | `[MEDICAL_RECORD_ID_1]` |

### Medical Term Whitelisting
SciSpaCy (BC5CDR corpus) runs alongside Presidio. If Presidio flags a string as `PERSON` but SciSpaCy classifies it as `DISEASE` or `CHEMICAL` with high confidence, **the entity is NOT masked**. This prevents clinical terms like "Parkinson's disease" from being redacted.

---

## 🔐 De-Masking Modes

| Mode | Behaviour | Best For |
|------|-----------|---------|
| **Restore Mode** | Swaps placeholders back to original values via Token Registry | Attending physician summaries |
| **Generic Mode** | Replaces placeholders with role labels ("the patient", "the physician") | Research, training datasets, secondary tasks |

---

## 📊 Evaluation Design

The system is evaluated on **synthetic healthcare prompts** (no real patient data) across two dimensions:

### Privacy Metrics
- **PII Recall** — fraction of true PII entities detected and masked
- **PII Precision** — fraction of detected entities that are actually PII
- **Masking Success Rate** — detected entities successfully replaced with placeholders
- **PII Leakage Rate** — original PII values remaining in the anonymized prompt (target: 0)

### Utility Metrics
LLM responses are scored 1–5 across: Relevance, Completeness, Coherence, Context Preservation, Placeholder Handling, Hallucination Risk, Medical Safety

### Baseline Comparison

| Condition | Privacy | Expected Utility |
|-----------|---------|-----------------|
| Original Prompt (no masking) | ❌ Low | ✅ High |
| Full Redaction `[REDACTED]` | ✅ High | ⚠️ Low–Medium |
| **Placeholder Masking (ours)** | ✅ High | ✅ Medium–High |

---

## 🗂️ Repo Structure

```
SystemX/
│
├── proxy/
│   ├── request_handler.py        # Entry point — receives raw prompt
│   ├── ner_pipeline.py           # Hybrid PII detection (Presidio + SciSpaCy)
│   ├── masking_engine.py         # Placeholder substitution
│   ├── mapping_vault.py          # In-memory token registry
│   ├── policy_engine.py          # Safety check before LLM call
│   ├── prompt_builder.py         # Constructs final masked prompt
│   ├── llm_gateway.py            # HTTPS call to public LLM API
│   ├── response_validator.py     # Local validation of LLM output
│   └── de_anonymizer.py          # Restore or Generic mode de-masking
│
├── evaluation/
│   ├── synthetic_prompts.json    # Annotated test dataset
│   └── eval_metrics.py           # PII recall, precision, leakage rate, quality score
│
├── requirements.txt
├── .gitignore
└── README.md
```

> ⚠️ Folder structure reflects planned implementation — files will be added as development progresses.

---

## 🚀 Getting Started *(planned)*

```bash
git clone https://github.com/YOUR_USERNAME/SystemX-PII-Proxy.git
cd SystemX-PII-Proxy
pip install -r requirements.txt
```

Set your LLM API key (never stored in the repo):
```bash
export ANTHROPIC_API_KEY=your_key_here
# or
export OPENAI_API_KEY=your_key_here
```

Run the proxy on a test prompt:
```bash
python proxy/request_handler.py --prompt "Anna Müller, born 12.03.1980, has Type 2 diabetes. Summarize her treatment."
```

---

## 📦 Key Dependencies *(planned)*

```
# NLP / PII Detection
presidio-analyzer
presidio-anonymizer
spacy
scispacy
https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_ner_bc5cdr_md-0.5.3.tar.gz

# LLM API
anthropic   # or openai

# Evaluation
sentence-transformers   # semantic similarity scoring
scikit-learn            # precision / recall metrics
```

---

## ⚖️ Regulatory Context

| Framework | Relevant Rule | System Response |
|---|---|---|
| HIPAA | Safe Harbour — 18 specific identifiers must be removed | Direct target entity set for NER component |
| GDPR Art. 29 WP216 | Anonymization = irreversible prevention of singling out, linkability, inference | Motivates re-identification risk measurement as evaluation criterion |

> **Disclaimer:** This is an academic prototype. It does not constitute legal HIPAA/GDPR compliance certification. Real deployment would require institutional review, legal audit, and organizational controls.

---

## 📚 Key References

1. Chong et al., "Casper: Prompt Sanitization for Protecting User Privacy in Web-Based LLMs," CSCloud 2025
2. Chen et al., "Hide and Seek (HaS): A Lightweight Framework for Prompt Privacy Protection," 2023
3. HHS, "HIPAA De-identification Guidance," 2012
4. Article 29 Working Party, Opinion WP216 on Anonymisation Techniques, 2014
5. Manzanares-Salor et al., "Evaluating Re-identification Risk of Anonymized Documents," DMKD 2024
# privacy-preserving-llm-inference
