def detect_medical_entities_with_scispacy(text): 
    """ 
    Optional SciSpaCy BC5CDR detector. 
 
    Detects biomedical entities such as diseases and chemicals. 
    These are not direct PII. They help preserve clinical context. 
    """ 
 
    try: 
        import spacy 
        nlp = spacy.load("en_ner_bc5cdr_md") 
    except Exception: 
        return [] 
 
    doc = nlp(text) 
 
    entities = [] 
 
    for ent in doc.ents: 
        entities.append({ 
            "text": ent.text, 
            "type": f"MEDICAL_{ent.label_}", 
            "start": ent.start_char, 
            "end": ent.end_char, 
            "confidence": None, 
            "source": "scispacy_bc5cdr" 
        }) 
 
    return entities