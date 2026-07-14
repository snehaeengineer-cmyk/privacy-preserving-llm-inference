def detect_pii_with_spacy(text):
    """
    Optional spaCy-based detector.

    This function tries to use spaCy NER to detect extra entities.
    If spaCy or the model is not installed, it returns an empty list
    so the project still works.
    """

    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        return []

    doc = nlp(text)

    entities = []

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entity_type = "PERSON_SPACY"
        elif ent.label_ == "GPE":
            entity_type = "LOCATION_SPACY"
        elif ent.label_ == "ORG":
            entity_type = "ORG_SPACY"
        elif ent.label_ == "DATE":
            entity_type = "DATE_SPACY"
        else:
            continue

        entities.append({
            "text": ent.text,
            "type": entity_type,
            "start": ent.start_char,
            "end": ent.end_char,
            "source": "spacy"
        })

    return entities