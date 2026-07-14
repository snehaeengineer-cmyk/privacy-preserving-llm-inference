def detect_pii_with_presidio(text): 
    """ 
    Microsoft Presidio detector. 
 
    Presidio adds a general-purpose PII detection layer. 
    If Presidio fails, this function returns an empty list so the prototype still runs. 
    """ 
 
    try: 
        from presidio_analyzer import AnalyzerEngine 
    except Exception: 
        return [] 
 
    try: 
        analyzer = AnalyzerEngine() 
        results = analyzer.analyze(text=text, language="en") 
    except Exception: 
        return [] 
 
    entities = [] 
 
    type_mapping = { 
        "PERSON": "PERSON_PRESIDIO", 
        "LOCATION": "LOCATION_PRESIDIO", 
        "EMAIL_ADDRESS": "EMAIL", 
        "PHONE_NUMBER": "PHONE", 
        "DATE_TIME": "DATE_PRESIDIO", 
        "ORGANIZATION": "ORG_PRESIDIO", 
        "URL": "URL_PRESIDIO", 
        "IP_ADDRESS": "IP_ADDRESS_PRESIDIO", 
    } 
 
    for item in results: 
       detected_text = text[item.start:item.end] 
 
        # Treat age expressions as quasi-identifiers, not direct dates. 
        # This preserves clinical meaning while allowing the Policy Engine to warn. 
    if "year-old" in detected_text.lower() or detected_text.lower().startswith("age "): 
            mapped_type = "AGE_QUASI" 
    else: 
            mapped_type = type_mapping.get(item.entity_type, f"{item.entity_type}_PRESIDIO")
 
    entities.append({ 
            "text": detected_text, 
            "type": mapped_type, 
            "start": item.start, 
            "end": item.end, 
            "confidence": round(item.score, 3), 
            "source": "presidio" 
        }) 
 
    return entities 