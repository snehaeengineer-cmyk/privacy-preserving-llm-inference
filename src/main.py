import os
import pandas as pd 

from request_handler import process_user_request 

def main(): 
    """ 
    Entry point for the architecture-aligned anonymization proxy prototype. 
    Loads synthetic prompts, sends each prompt to the Request Handler, 
    and saves the result metadata to outputs/results.csv. 
    """ 

    input_path = "data/synthetic_prompts.csv" 
    output_path = "outputs/results.csv" 
     
    os.makedirs("outputs", exist_ok=True) 
     
    df = pd.read_csv(input_path) 
     
    results = [] 
     
    for _, row in df.iterrows(): 
        prompt_id = row["prompt_id"] 
        task_type = row["task_type"] 
        prompt = row["prompt"] 
     
        print("\n" + "=" * 80) 
        print(f"Processing prompt ID: {prompt_id}") 
     
        result = process_user_request( 
            prompt_id=prompt_id, 
            task_type=task_type, 
            prompt=prompt, 
            demasking_mode="generic" 
        ) 
     
        results.append(result) 
     
        print("Status:", result.get("status")) 
        print("Policy decision:", result.get("policy_decision")) 
        print("Validator decision:", result.get("validator_decision")) 
        print("Final output:", result.get("final_response")) 
     
    results_df = pd.DataFrame(results) 
    results_df.to_csv(output_path, index=False, encoding="utf-8") 
     
    print("\n" + "=" * 80) 
    print("Processing complete.") 
    print(f"Results saved to {output_path}") 
 
if __name__ == "__main__": 
    main()