def spans_overlap(entity_a, entity_b): 
    """ 
    Check whether two detected entity spans overlap. 
    """ 
    return not ( 
        entity_a["end"] <= entity_b["start"] 
        or entity_b["end"] <= entity_a["start"] 
    ) 
 
 
def entity_priority(entity): 
    """ 
    Higher number = stronger priority. 
 
    Priority logic: 
    - Structured identifiers are highest priority. 
    - Known dataset labels are strong. 
    - Medical entities should be preserved and can override weak general NER. 
    - Presidio/spaCy general entities are lower priority. 
    """ 
 
    entity_type = entity.get("type", "") 
    source = entity.get("source", "") 
 
    structured_types = { 
        "EMAIL", 
        "PHONE", 
        "DATE_OF_BIRTH", 
        "APPOINTMENT_DATE", 
        "INSURANCE_ID", 
        "MEDICAL_RECORD_ID", 
        "ADDRESS", 
    } 
 
    known_direct_types = { 
        "PATIENT_NAME", 
        "DOCTOR_NAME", 
        "LOCATION", 
        "HOSPITAL", 
    } 
 
    if entity_type in structured_types: 
        return 100 
 
    if entity_type in known_direct_types: 
        return 90 
 
    if entity_type.startswith("MEDICAL_"): 
        return 80 
 
    if source == "presidio": 
        return 60 
 
    if source == "spacy": 
        return 50 
 
    return 10 
 
 
def resolve_conflicts(entities): 
    """ 
    Resolve overlapping detections from regex, known lists, spaCy, Presidio, and SciSpaCy. 
 
    The goal is to avoid double masking and preserve medical context. 
    """ 
 
    if not entities: 
        return [] 
 
    # Sort by priority first, then longer span 
    sorted_entities = sorted( 
        entities, 
        key=lambda e: ( 
            entity_priority(e), 
            e["end"] - e["start"] 
        ), 
        reverse=True 
    ) 
 
    selected = [] 
 
    for candidate in sorted_entities: 
        conflict_found = False 
 
        for selected_entity in selected: 
            if spans_overlap(candidate, selected_entity): 
                conflict_found = True 
                break 
 
        if not conflict_found: 
            selected.append(candidate) 
 
    # Return in text order 
    selected = sorted(selected, key=lambda e: e["start"]) 
 
    return selected 
