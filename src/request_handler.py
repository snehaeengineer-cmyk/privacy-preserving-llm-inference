from anonymization_session import create_session 

from pii_detection_engine import detect_pii 

from masking_engine import mask_text 

from mapping_vault import create_mapping_vault, delete_mapping_vault 

from policy_engine import check_policy 

from prompt_builder import build_llm_prompt 

from llm_gateway import send_to_llm 

from response_handler import handle_llm_response 

from baselines import full_redaction 

from mock_llm import mock_llm 

from audit_logger import log_event 

  

  

def process_user_request(prompt_id, task_type, prompt, demasking_mode="generic"): 

    """ 

    Full request pipeline for the privacy-preserving LLM proxy. 

  

    Steps: 

    1. Create anonymization session 

    2. Detect PII and biomedical entities 

    3. Create redaction baseline 

    4. Mask direct identifiers 

    5. Store mapping in local session vault 

    6. Run policy check 

    7. Send masked prompt to LLM gateway 

    8. Validate and handle LLM response 

    9. Delete mapping vault after response handling 

    10. Return evaluation-friendly result dictionary 

  

    Note: 

    The mapping is still written into results for prototype evaluation. 

    In production, the mapping field should not be exported. 

    """ 

  

    session = create_session( 

        prompt_id=prompt_id, 

        task_type=task_type, 

        demasking_mode=demasking_mode 

    ) 

  

    log_event( 

        session["session_id"], 

        prompt_id, 

        "SESSION_CREATED", 

        "New anonymization session created." 

    ) 

  

    detected_entities = detect_pii(prompt) 

  

    log_event( 

        session["session_id"], 

        prompt_id, 

        "PII_DETECTED", 

        f"Detected {len(detected_entities)} entities." 

    ) 

  

    redacted_prompt = full_redaction(prompt, detected_entities) 

  

    masked_prompt, mapping = mask_text(prompt, detected_entities) 

  

    vault = create_mapping_vault(session["session_id"], mapping) 

  

    log_event( 

        session["session_id"], 

        prompt_id, 

        "PROMPT_MASKED", 

        "Prompt was masked and mapping was stored in local session vault." 

    ) 

  

    policy_result = check_policy(masked_prompt, detected_entities)

  

    log_event( 

        session["session_id"], 

        prompt_id, 

        "POLICY_CHECK", 

        f"Policy decision: {policy_result['decision']}" 

    ) 

  

    # Baseline responses for evaluation 

    # These always use mock_llm so the baseline remains stable and reproducible. 

    original_response = mock_llm(prompt) 

    redacted_response = mock_llm(redacted_prompt) 

  

    if policy_result["decision"] == "BLOCK": 

        final_result = { 

            "prompt_id": prompt_id, 

            "task_type": task_type, 

            "original_prompt": prompt, 

            "status": "blocked_by_policy", 

            "session_id": session["session_id"], 

            "detected_entities": str(detected_entities), 

            "masked_prompt": masked_prompt, 

            "redacted_prompt": redacted_prompt, 

            "mapping": str(mapping), 

            "policy_decision": policy_result["decision"], 

            "policy_violations": str(policy_result.get("violations", [])), 

            "policy_warnings": str(policy_result.get("warnings", [])), 

            "quasi_identifier_risk_level": policy_result.get( 

                "quasi_identifier_risk_level", 

                "" 

            ), 

            "quasi_identifier_risk_factors": str( 

                policy_result.get("quasi_identifier_risk_factors", []) 

            ), 

            "llm_prompt": "", 

            "original_response": original_response, 

            "redacted_response": redacted_response, 

            "placeholder_response": "", 

            "validator_decision": "", 

            "validator_issues": str([]), 

            "demasking_mode": demasking_mode, 

            "final_response": "" 

        } 

  

        delete_mapping_vault(vault) 

  

        log_event( 

            session["session_id"], 

            prompt_id, 

            "MAPPING_VAULT_DELETED", 

            "Session mapping vault was deleted after policy block." 

        ) 

  

        return final_result 

  

    llm_prompt = build_llm_prompt(masked_prompt) 

  

    placeholder_response = send_to_llm(llm_prompt) 

  

    log_event( 

        session["session_id"], 

        prompt_id, 

        "LLM_RESPONSE_RECEIVED", 

        "Received response from LLM gateway." 

    ) 

  

    response_result = handle_llm_response( 

        session=session, 

        masked_prompt=masked_prompt, 

        llm_response=placeholder_response, 

        vault=vault, 

        demasking_mode=demasking_mode 

    ) 

  

    log_event( 

        session["session_id"], 

        prompt_id, 

        "RESPONSE_HANDLED", 

        f"Validator decision: {response_result['validator_decision']}" 

    ) 

  

    final_result = { 

        "prompt_id": prompt_id, 

        "task_type": task_type, 

        "original_prompt": prompt, 

        "status": response_result["status"], 

        "session_id": session["session_id"], 

        "detected_entities": str(detected_entities), 

        "masked_prompt": masked_prompt, 

        "redacted_prompt": redacted_prompt, 

        "mapping": str(mapping), 

        "policy_decision": policy_result["decision"], 

        "policy_violations": str(policy_result.get("violations", [])), 

        "policy_warnings": str(policy_result.get("warnings", [])), 

        "quasi_identifier_risk_level": policy_result.get( 

            "quasi_identifier_risk_level", 

            "" 

        ), 

        "quasi_identifier_risk_factors": str( 

            policy_result.get("quasi_identifier_risk_factors", []) 

        ), 

        "llm_prompt": llm_prompt, 

        "original_response": original_response, 

        "redacted_response": redacted_response, 

        "placeholder_response": placeholder_response, 

        "validator_decision": response_result["validator_decision"], 

        "validator_issues": str(response_result.get("validator_issues", [])), 

        "demasking_mode": demasking_mode, 

        "final_response": response_result["final_response"] 

    } 

  

    delete_mapping_vault(vault) 

  

    log_event( 

        session["session_id"], 

        prompt_id, 

        "MAPPING_VAULT_DELETED", 

        "Session mapping vault was deleted after response handling." 

    ) 

  

    return final_result 