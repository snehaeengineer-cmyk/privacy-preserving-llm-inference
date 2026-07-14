import re 

  

from quasi_identifier import detect_quasi_identifiers 

  

  

def check_low_confidence_entities(detected_entities, threshold=0.5): 

    """ 

    Check for low-confidence entities from external NER tools. 

  

    This does not block the prompt. 

    It only creates warnings for possible unresolved PII. 

    """ 

  

    warnings = [] 

  

    risky_types = [ 

        "PERSON_PRESIDIO", 

        "LOCATION_PRESIDIO", 

        "ORG_PRESIDIO", 

        "DATE_PRESIDIO", 

        "PERSON_SPACY", 

        "LOCATION_SPACY", 

        "ORG_SPACY", 

        "DATE_SPACY", 

    ] 

  

    for entity in detected_entities: 

        entity_type = entity.get("type", "") 

        confidence = entity.get("confidence", None) 

  

        if confidence is None: 

            continue 

  

        if entity_type in risky_types and confidence < threshold: 

            warnings.append( 

                f"Low-confidence entity detected: " 

                f"{entity.get('text')} as {entity_type} " 

                f"(confidence={confidence})" 

            ) 

  

    return warnings 

  

  

def check_policy(masked_prompt, detected_entities=None): 

    """ 

    Check whether the masked prompt is safe enough to send to the LLM. 

  

    Decision logic: 

    - BLOCK if direct PII remains visible. 

    - WARN if quasi-identifiers create possible re-identification risk. 

    - WARN if low-confidence suspicious entities are detected. 

    - PASS if no obvious issue is detected. 

    """ 

  

    if detected_entities is None: 

        detected_entities = [] 

  

    violations = [] 

    warnings = [] 

  

    # Low-confidence warnings from Presidio/spaCy 

    low_confidence_warnings = check_low_confidence_entities(detected_entities) 

  

    if low_confidence_warnings: 

        warnings.extend(low_confidence_warnings) 

  

    # Check direct identifiers that should not remain visible 

  

    # Email pattern 

    if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", masked_prompt): 

        violations.append("Email still visible") 

  

    # German phone pattern 

    if re.search(r"\+49\s?\d{2,4}\s?\d{5,10}", masked_prompt): 

        violations.append("Phone number still visible") 

  

    # Exact date pattern 

    if re.search(r"\b\d{2}\.\d{2}\.\d{4}\b", masked_prompt): 

        violations.append("Exact date still visible") 

  

    # Insurance ID pattern 

    if re.search(r"\b[A-Z]\d{9}\b", masked_prompt): 

        violations.append("Insurance ID still visible") 

  

    # Medical record number pattern 

    if re.search(r"\bMRN-\d{6}\b", masked_prompt): 

        violations.append("Medical record number still visible") 

  

    # Street address pattern 

    if re.search(r"\b[A-Za-zäöüÄÖÜß]+straße\s\d+\b", masked_prompt): 

        violations.append("Street address still visible") 

  

    # If direct PII remains, block immediately 

    if violations: 

        return { 

            "decision": "BLOCK", 

            "violations": violations, 

            "warnings": warnings, 

            "quasi_identifier_risk_level": "NOT_EVALUATED", 

            "quasi_identifier_risk_factors": [] 

        } 

  

    # Check quasi-identifier risk after direct PII masking 

    quasi_result = detect_quasi_identifiers(masked_prompt) 

  

    risk_level = quasi_result["risk_level"] 

    risk_factors = quasi_result["risk_factors"] 

  

    if risk_level in ["MEDIUM", "HIGH"]: 

        warnings.append( 

            f"Quasi-identifier risk level {risk_level}: " 

            + "; ".join(risk_factors) 

        ) 

  

    # Final decision 

    if warnings: 

        decision = "WARN" 

    else: 

        decision = "PASS" 

  

    return { 

        "decision": decision, 

        "violations": [], 

        "warnings": warnings, 

        "quasi_identifier_risk_level": risk_level, 

        "quasi_identifier_risk_factors": risk_factors 

    } 