def full_redaction(text, entities):
    """
    Aggressive baseline that replaces detected PII and selected clinical terms with [REDACTED].
    This shows how too much redaction can reduce utility.
    """

    redacted_text = text

    # Replace detected PII entities
    entities = sorted(entities, key=lambda x: x["start"], reverse=True)

    for entity in entities:
        redacted_text = (
            redacted_text[:entity["start"]]
            + "[REDACTED]"
            + redacted_text[entity["end"]:]
        )

    # Aggressively redact some medical terms to simulate utility loss
    medical_terms = [
        "Type 2 diabetes",
        "diabetes",
        "hypertension",
        "Metformin",
        "insulin",
        "asthma",
        "inhaler",
        "chest pain",
        "HbA1c",
        "high cholesterol",
        "migraine",
        "Parkinson's disease",
        "pneumonia",
        "low hemoglobin",
        "knee pain",
        "dizziness"
    ]

    for term in medical_terms:
        redacted_text = redacted_text.replace(term, "[REDACTED]")

    return redacted_text