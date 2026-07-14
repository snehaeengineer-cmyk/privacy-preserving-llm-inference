import re
from conflict_resolver import resolve_conflicts 
try: 
    from presidio_detector import detect_pii_with_presidio 
except Exception: 
    detect_pii_with_presidio = None 
 
try: 
    from scispacy_detector import detect_medical_entities_with_scispacy 
except Exception: 
    detect_medical_entities_with_scispacy = None 

try:
    from spacy_detector import detect_pii_with_spacy
except Exception:
    detect_pii_with_spacy = None


def detect_pii(text):
    """
    Detect simple PII entities in a healthcare prompt.
    This prototype uses regex patterns and controlled known-entity lists.
    """

    entities = []

    # Detect dates like 12.03.1980 or 15.04.2026
    # We classify dates after checking context:
    # - "born" or "DOB" nearby -> DATE_OF_BIRTH
    # - "appointment" nearby -> APPOINTMENT_DATE
    for match in re.finditer(r"\b\d{2}\.\d{2}\.\d{4}\b", text):
        start = match.start()
        end = match.end()

        context_before = text[max(0, start - 30):start].lower()

        if "born" in context_before or "dob" in context_before:
            entity_type = "DATE_OF_BIRTH"
        elif "appointment" in context_before:
            entity_type = "APPOINTMENT_DATE"
        else:
            entity_type = "DATE"

        entities.append({
            "text": match.group(),
            "type": entity_type,
            "start": start,
            "end": end
        })

    # Detect German phone numbers like +49 176 12345678
    for match in re.finditer(r"\+49\s?\d{2,4}\s?\d{5,10}", text):
        entities.append({
            "text": match.group(),
            "type": "PHONE",
            "start": match.start(),
            "end": match.end()
        })

    # Detect email addresses
    for match in re.finditer(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", text):
        entities.append({
            "text": match.group(),
            "type": "EMAIL",
            "start": match.start(),
            "end": match.end()
        })

    # Detect simple insurance IDs like A123456789 or C112233445
    for match in re.finditer(r"\b[A-Z]\d{9}\b", text):
        entities.append({
            "text": match.group(),
            "type": "INSURANCE_ID",
            "start": match.start(),
            "end": match.end()
        })

    # Detect medical record numbers like MRN-883921
    for match in re.finditer(r"\bMRN-\d{6}\b", text):
        entities.append({
            "text": match.group(),
            "type": "MEDICAL_RECORD_ID",
            "start": match.start(),
            "end": match.end()
        })

    # Detect simple street addresses
    address_patterns = [
        r"\bLeopoldstraße\s\d+\b"
    ]

    for pattern in address_patterns:
        for match in re.finditer(pattern, text):
            entities.append({
                "text": match.group(),
                "type": "ADDRESS",
                "start": match.start(),
                "end": match.end()
            })

    # Known patient and doctor names for prototype dataset
    known_names = [
        # Existing names
        "Anna Müller",
        "John Smith",
        "Maria Becker",
        "Lukas Weber",
        "Sofia Klein",
        "Noah Fischer",
        "Emma Wagner",
        "Dr. Keller",
        "Paul Hoffmann",
        "Laura Schneider",
        "Dr. Braun",
        "Felix Weber",
        "Mia Becker",
        "Omar Ali",
        "Nina Koch",
        "David Richter",
        "Dr. Hoffmann",
        "Lina Bauer",
        "Dr. Schmidt",

        # New names P016-P030
        "Karl Parkinson",
        "Dr. Green",
        "Laura Stein",
        "Thomas Wolf",
        "Clara Weber",
        "Otto Meyer",
        "Hannah Koch",
        "Dr. Vogel",
        "Ben Wagner",
        "Peter Lang",
        "Sara Klein",
        "Dr. Neumann",
        "Julia Braun",
        "Mark Fischer",
        "Leo Hoffmann",
        "Greta Schmid",
        "Emil Wagner",
        "Dr. Becker",
        "Alina Wolf"
    ]

    for name in known_names:
        start = text.find(name)
        if start != -1:
            entity_type = "DOCTOR_NAME" if name.startswith("Dr.") else "PATIENT_NAME"
            entities.append({
                "text": name,
                "type": entity_type,
                "start": start,
                "end": start + len(name)
            })

    # Known locations for prototype dataset
    known_locations = [
        "Munich",
        "Berlin",
        "Hamburg",
        "Cologne",
        "Stuttgart",
        "Garmisch",
        "Augsburg",
        "Nuremberg",
        "Regensburg",
        "Rosenheim",
        "Dresden"
    ]

    for location in known_locations:
        start = text.find(location)
        if start != -1:
            entities.append({
                "text": location,
                "type": "LOCATION",
                "start": start,
                "end": start + len(location)
            })

    # Known hospitals / organizations
    known_hospitals = [
        "Klinikum rechts der Isar",
        "Charité Berlin"
    ]

    for hospital in known_hospitals:
        start = text.find(hospital)
        if start != -1:
            entities.append({
                "text": hospital,
                "type": "HOSPITAL",
                "start": start,
                "end": start + len(hospital)
            })

        # Optional spaCy detection
    if detect_pii_with_spacy is not None:
        spacy_entities = detect_pii_with_spacy(text)
        entities.extend(spacy_entities)
    if detect_pii_with_presidio is not None: 
        entities.extend(detect_pii_with_presidio(text)) 
 
    # Optional SciSpaCy biomedical layer 
    # These are included for analysis/context preservation, not direct PII masking. 
    if detect_medical_entities_with_scispacy is not None: 
        entities.extend(detect_medical_entities_with_scispacy(text)) 

    # Remove duplicate entities with same text/start/end/type
    unique_entities = [] 
    seen = set() 
 
    for entity in entities: 
        key = ( 
            entity.get("text"), 
            entity.get("start"), 
            entity.get("end"), 
            entity.get("type"), 
            entity.get("source", "") 
        ) 
 
        if key not in seen: 
            seen.add(key) 
            unique_entities.append(entity) 
 
    # Resolve overlapping/conflicting detections 
    resolved_entities = resolve_conflicts(unique_entities) 
 
    return resolved_entities
