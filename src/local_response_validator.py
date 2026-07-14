import re 

  

  

def validate_response(response_text): 

    """ 

    Local Response Validator. 

  

    Checks the masked LLM response before de-masking or final output. 

    This is a lightweight safety and leakage guardrail, not a medical fact checker. 

    """ 

  

    issues = [] 

  

    # Email leakage 

    if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", response_text): 

        issues.append("Email-like pattern found in LLM response") 

  

    # German phone leakage 

    if re.search(r"\+49\s?\d{2,4}\s?\d{5,10}", response_text): 

        issues.append("Phone-like pattern found in LLM response") 

  

    # Exact date leakage 

    if re.search(r"\b\d{2}\.\d{2}\.\d{4}\b", response_text): 

        issues.append("Exact date-like pattern found in LLM response") 

  

    # Insurance ID leakage 

    if re.search(r"\b[A-Z]\d{9}\b", response_text): 

        issues.append("Insurance ID-like pattern found in LLM response") 

  

    # Medical record number leakage 

    if re.search(r"\bMRN-\d{6}\b", response_text): 

        issues.append("Medical record number-like pattern found in LLM response") 

  

    # Unsafe medical advice examples 

    unsafe_phrases = [ 

        "stop taking medication", 

        "double the dose", 

        "ignore your doctor", 

        "do not consult a doctor" 

    ] 

  

    for phrase in unsafe_phrases: 

        if phrase in response_text.lower(): 

            issues.append(f"Unsafe medical phrase found: {phrase}") 

  

    if issues: 

        return { 

            "decision": "BLOCK", 

            "issues": issues 

        } 

  

    return { 

        "decision": "PASS", 

        "issues": [] 

    } 