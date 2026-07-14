import re 

  

  

def final_output_check(final_text): 

    """ 

    Final Output Filter. 

  

    Performs a last leakage check after generic/restore mode. 

    """ 

  

    issues = [] 

  

    if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", final_text): 

        issues.append("Email-like pattern found in final output") 

  

    if re.search(r"\+49\s?\d{2,4}\s?\d{5,10}", final_text): 

        issues.append("Phone-like pattern found in final output") 

  

    if re.search(r"\b[A-Z]\d{9}\b", final_text): 

        issues.append("Insurance ID-like pattern found in final output") 

  

    if re.search(r"\bMRN-\d{6}\b", final_text): 

        issues.append("Medical record number-like pattern found in final output") 

  

    if issues: 

        return { 

            "decision": "BLOCK", 

            "issues": issues 

        } 

  

    return { 

        "decision": "PASS", 

        "issues": [] 

    }