from local_response_validator import validate_response 

from de_anonymizer import de_anonymize_response 

from final_output_filter import final_output_check 

  

  

def handle_llm_response(session, masked_prompt, llm_response, vault, demasking_mode="generic"): 

    """ 

    Response Handler. 

  

    Validates the LLM response, applies generic/restore de-anonymization, 

    and performs final output filtering. 

    """ 

  

    validation_result = validate_response(llm_response) 

  

    if validation_result["decision"] == "BLOCK": 

        return { 

            "status": "blocked_by_validator", 

            "validator_decision": validation_result["decision"], 

            "validator_issues": validation_result["issues"], 

            "final_response": "" 

        } 

  

    final_response = de_anonymize_response( 

        response_text=llm_response, 

        vault=vault, 

        mode=demasking_mode 

    ) 

  

    final_filter_result = final_output_check(final_response) 

  

    if final_filter_result["decision"] == "BLOCK": 

        return { 

            "status": "blocked_by_final_output_filter", 

            "validator_decision": "PASS", 

            "validator_issues": final_filter_result["issues"], 

            "final_response": "" 

        } 

  

    return { 

        "status": "success", 

        "validator_decision": validation_result["decision"], 

        "validator_issues": validation_result["issues"], 

        "final_response": final_response 

    }