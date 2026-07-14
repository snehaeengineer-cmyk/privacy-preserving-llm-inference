import os
from request_handler import process_user_request 

def main(): 
    prompt_id = "DEMO_001" 
    task_type = "clinical_summary" 

    prompt = ( 
     "Emma Wagner, born on 21.11.1975, has knee pain and an appointment with Dr. Keller. Prepare an appointment summary."
       
    ) 
     
    result = process_user_request( 
        prompt_id=prompt_id, 
        task_type=task_type, 
        prompt=prompt, 
        demasking_mode="generic" 
    ) 
     
    print("\n" + "=" * 80) 
    print("LIVE DEMO: PRIVACY-PRESERVING LLM PROXY") 
    print("=" * 80) 
     
    print("\n1. Original Prompt") 
    print("------------------") 
    print(result.get("original_prompt")) 
     
    print("\n2. Detected Entities") 
    print("--------------------") 
    print(result.get("detected_entities")) 
     
    print("\n3. Masked Prompt") 
    print("----------------") 
    print(result.get("masked_prompt")) 
     
    print("\n4. Policy Decision") 
    print("------------------") 
    print("Decision:", result.get("policy_decision")) 
    print("Violations:", result.get("policy_violations")) 
    print("Warnings:", result.get("policy_warnings")) 
    print("Quasi-Identifier Risk:", result.get("quasi_identifier_risk_level")) 
     
    print("\n5. LLM Prompt Sent Outside Trusted Boundary") 
    print("------------------------------------------") 
    print(result.get("llm_prompt")) 
     
    print("\n6. LLM Response") 
    print("--------------------") 
    print(result.get("placeholder_response")) 
     
    print("\n7. Local Validator") 
    print("------------------") 
    print("Validator decision:", result.get("validator_decision")) 
    print("Validator issues:", result.get("validator_issues")) 
     
    print("\n8. Final Response") 
    print("-----------------") 
    print(result.get("final_response")) 
     
    print("\n9. Audit Log") 
    print("------------") 
    print("Metadata-only audit log saved in outputs/audit_log.csv") 
     
    print("\n" + "=" * 80) 
 
if __name__ == "__main__": 
    main()