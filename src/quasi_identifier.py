import re 

  

  

RARE_DISEASES = [ 

    "huntington's disease", 

    "als", 

    "amyotrophic lateral sclerosis", 

    "rare cancer", 

    "wilson disease" 

] 

  

  

OCCUPATION_TERMS = [ 
    "teacher", 
    "school teacher", 
    "mayor", 
    "police officer", 
    "engineer", 
    "professor" 
] 
#Remove: doctor, nurse.  In your dataset, doctor names are already masked as DOCTOR_NAME. 
# The word doctor inside a placeholder should not create a quasi-identifier warning.

  

  

SMALL_LOCATION_TERMS = [ 

    "small village", 

    "village", 

    "near garmisch", 

    "near rosenheim" 

] 

  

  

GENDER_TERMS = [ 

    "male", 

    "female", 

    "woman", 

    "man" 

] 

  

  

PREGNANCY_TERMS = [ 

    "pregnant", 

    "pregnancy" 

] 

  

  

def detect_quasi_identifiers(text): 

    """ 

    Detect quasi-identifiers and combinations that may increase re-identification risk. 

  

    Quasi-identifiers are not always direct PII, but combinations such as 

    old age + gender + rare disease + small location may make a patient easier to identify. 

    """ 

  

    text_lower = text.lower() 

  

    risk_factors = [] 

  

    # Age detection: e.g., 32-year-old, 91-year-old 

    age_matches = re.findall(r"\b(\d{1,3})-year-old\b", text_lower) 

  

    for age_text in age_matches: 

        age = int(age_text) 

  

        if age >= 85: 

            risk_factors.append(f"Very old age: {age}") 

        elif age < 18: 

            risk_factors.append(f"Child age: {age}") 

        else: 

            risk_factors.append(f"Age mentioned: {age}") 

  

    # Gender detection 

    for term in GENDER_TERMS: 

        if re.search(rf"\b{re.escape(term)}\b", text_lower): 

            risk_factors.append(f"Gender mentioned: {term}") 

            break 

  

    # Pregnancy detection 

    for term in PREGNANCY_TERMS: 

        if term in text_lower: 

            risk_factors.append("Pregnancy mentioned") 

            break 

  

    # Occupation detection 

    for occupation in OCCUPATION_TERMS: 

        if occupation in text_lower: 

            risk_factors.append(f"Occupation mentioned: {occupation}") 

            break 

  

    # Rare disease detection 

    for disease in RARE_DISEASES: 

        if disease in text_lower: 

            risk_factors.append(f"Rare disease mentioned: {disease}") 

            break 

  

    # Small location detection 

    for location_term in SMALL_LOCATION_TERMS: 

        if location_term in text_lower: 

            risk_factors.append(f"Small location context: {location_term}") 

            break 

  

    # Hospital / organization context 

    hospital_terms = [ 

        "klinikum rechts der isar", 

        "charité berlin" 

    ] 

  

    for hospital in hospital_terms: 

        if hospital in text_lower: 

            risk_factors.append(f"Hospital mentioned: {hospital}") 

            break 

  

    # Determine risk level 

    risk_count = len(risk_factors) 

  

    # High-risk combinations 

    has_rare_disease = any("Rare disease" in factor for factor in risk_factors) 

    has_small_location = any("Small location" in factor for factor in risk_factors) 

    has_very_old_age = any("Very old age" in factor for factor in risk_factors) 

    has_child_age = any("Child age" in factor for factor in risk_factors) 

    has_gender = any("Gender" in factor for factor in risk_factors) 

    has_pregnancy = any("Pregnancy" in factor for factor in risk_factors) 

    has_occupation = any("Occupation" in factor for factor in risk_factors) 

  

    if ( 

        (has_rare_disease and has_small_location) 

        or (has_rare_disease and has_very_old_age) 

        or (has_very_old_age and has_gender and has_small_location) 

        or (has_child_age and has_small_location) 

    ): 

        risk_level = "HIGH" 

    elif ( 

        has_pregnancy 

        or has_occupation 

        or risk_count >= 2 

    ): 

        risk_level = "MEDIUM" 

    elif risk_count == 1: 

        risk_level = "LOW" 

    else: 

        risk_level = "NONE" 

  

    return { 

        "risk_level": risk_level, 

        "risk_factors": risk_factors 

    } 

 

 

 