from mapping_vault import get_mapping 

  

  

def de_anonymize_response(response_text, vault, mode="generic"): 

    """ 

    De-Anonymizer. 

  

    Supports two modes: 

    - generic: replace placeholders with general role labels. 

    - restore: replace placeholders with original values from the mapping vault. 

    """ 

  

    mapping = get_mapping(vault) 

    final_text = response_text 

  

    if mode == "restore": 

        for placeholder, original_value in mapping.items(): 

            final_text = final_text.replace(placeholder, original_value) 

  

        return final_text 

  

    # Generic mode: safer mode for this prototype 

    generic_replacements = { 

        "PATIENT_NAME": "the patient", 

        "DOCTOR_NAME": "the physician", 

        "LOCATION": "the location", 

        "ADDRESS": "the address", 

        "HOSPITAL": "the hospital", 

        "EMAIL": "the email address", 

        "PHONE": "the phone number", 

        "INSURANCE_ID": "the insurance identifier", 

        "MEDICAL_RECORD_ID": "the medical record identifier", 

        "DATE_OF_BIRTH": "the age group", 

        "APPOINTMENT_DATE": "the appointment date", 

        "ORG_SPACY": "the organization", 

        "PERSON_SPACY": "the person", 

        "LOCATION_SPACY": "the location", 

        "DATE_SPACY": "the date" 

    } 

  

    for placeholder in mapping.keys(): 

        clean_key = placeholder.strip("[]") 

  

        # Example: PATIENT_NAME_1 -> PATIENT_NAME 

        parts = clean_key.split("_") 

        if len(parts) > 1 and parts[-1].isdigit(): 

            base_type = "_".join(parts[:-1]) 

        else: 

            base_type = clean_key 

  

        replacement = generic_replacements.get(base_type, "the masked entity") 

        final_text = final_text.replace(placeholder, replacement) 

 # Small grammar cleanup after generic replacement
    final_text = final_text.replace("Patient the patient", "The patient")
    final_text = final_text.replace("patient the patient", "The patient")
    final_text = final_text.replace("Doctor the physician", "The physician")
    final_text = final_text.replace("doctor the physician", "The physician")

    return final_text  