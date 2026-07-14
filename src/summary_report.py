import ast 
import os 
import pandas as pd 

def safe_parse_list_or_dict(value):
    """
    Convert string representation of list/dict back into Python object.
    If parsing fails, return an empty list.
    """
    try:
        return ast.literal_eval(value)
    except Exception:
        return []

def create_summary(): 
    """ Create a detailed statistics summary for the anonymization proxy prototype. """ 

    results_path = "outputs/results.csv" 
    privacy_path = "outputs/privacy_evaluation.csv" 
    output_path = "outputs/evaluation_summary.txt" 
     
    os.makedirs("outputs", exist_ok=True) 
     
    results_df = pd.read_csv(results_path) 
    privacy_df = pd.read_csv(privacy_path) 
     
    # Basic counts 
    total_prompts = len(results_df) 
    successful_prompts = len(results_df[results_df["status"] == "success"]) 
     
    # Privacy metrics 
    total_ground_truth = privacy_df["ground_truth_count"].sum() 
    total_correct = privacy_df["correctly_detected_count"].sum() 
    total_leaked = privacy_df["leaked_pii_count"].sum() 
     
    avg_recall = privacy_df["pii_recall"].mean() 
    avg_leakage = privacy_df["leakage_rate"].mean() 
     
    # Policy decision counts 
    policy_counts = results_df["policy_decision"].value_counts().to_dict() 
     
    pass_count = policy_counts.get("PASS", 0) 
    warn_count = policy_counts.get("WARN", 0) 
    block_count = policy_counts.get("BLOCK", 0) 
     
    # Quasi-identifier risk counts 
    if "quasi_identifier_risk_level" in results_df.columns: 
        quasi_counts = results_df["quasi_identifier_risk_level"].value_counts().to_dict() 
    else: 
        quasi_counts = {} 
     
    # Entity type counts 
    entity_type_counts = {} 
     
    for _, row in results_df.iterrows(): 
        detected_entities = safe_parse_list_or_dict(row["detected_entities"]) 
     
        for entity in detected_entities: 
            entity_type = entity.get("type", "UNKNOWN") 
            entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1 
     
    utility_path = "outputs/utility_evaluation_template.csv" 

  

    utility_summary_text = "Utility evaluation file not found." 

  

    if os.path.exists(utility_path) and os.path.getsize(utility_path) > 0: 

        try: 

            utility_df = pd.read_csv(utility_path) 

  

            if "overall_score" in utility_df.columns: 

                scored_utility_df = utility_df.dropna(subset=["overall_score"]).copy() 

  

                if len(scored_utility_df) > 0: 

                    scored_utility_df["overall_score"] = pd.to_numeric( 

                        scored_utility_df["overall_score"], 

                        errors="coerce" 

                    ) 

  

                    utility_by_condition = ( 

                        scored_utility_df 

                        .groupby("condition")["overall_score"] 

                        .mean() 

                        .round(2) 

                        .to_dict() 

                    ) 

  

                    utility_summary_text = "Average utility score by condition:\n" 

                    for condition, score in utility_by_condition.items(): 

                        utility_summary_text += f"- {condition}: {score}\n" 

                else: 

                    utility_summary_text = "Utility evaluation file exists, but no scores are filled yet." 

            else: 

                utility_summary_text = "Utility evaluation file exists, but it has no overall_score column." 

  

        except pd.errors.EmptyDataError: 

            utility_summary_text = "Utility evaluation file exists, but it is empty." 

    else: 

        utility_summary_text = "Utility evaluation file not found or empty."    # Build entity count text 
    entity_count_text = "" 
    for entity_type, count in sorted(entity_type_counts.items()): 
        entity_count_text += f"- {entity_type}: {count}\n" 
     
    # Build policy count text 
    policy_count_text = "" 
    policy_count_text += f"- PASS: {pass_count}\n" 
    policy_count_text += f"- WARN: {warn_count}\n" 
    policy_count_text += f"- BLOCK: {block_count}\n" 
     
    # Build quasi-identifier risk text 
    quasi_count_text = "" 
    if quasi_counts: 
        for risk_level, count in sorted(quasi_counts.items()): 
            quasi_count_text += f"- {risk_level}: {count}\n" 
    else: 
        quasi_count_text = "- No quasi-identifier risk data available.\n" 
     
    report = f""" 
Privacy-Preserving LLM Proxy - Detailed Evaluation Summary 

Dataset Overview 
Total prompts processed: {total_prompts}
Successful prompts: {successful_prompts} 

Privacy Evaluation 
Total ground truth PII entities: {total_ground_truth}
Correctly detected PII entities: {total_correct}
Leaked PII entities in masked prompts: {total_leaked} 

Average PII recall: {avg_recall:.3f}
Average leakage rate: {avg_leakage:.3f} 

Detected Entity Type Counts 
{entity_count_text} 

Policy Decision Counts 
{policy_count_text} 

Quasi-Identifier Risk Counts 
{quasi_count_text} 

Utility Evaluation Summary 
{utility_summary_text} 

Interpretation 
The current prototype demonstrates an end-to-end anonymization pipeline for synthetic healthcare prompts. The system detects direct identifiers, replaces them with typed placeholders or generalized values, applies policy checks, compares placeholder-based masking against a full-redaction baseline, and evaluates privacy using labeled ground truth annotations. 

The privacy metrics should be interpreted as controlled feasibility results because the dataset is synthetic and the current detector relies on rule-based patterns and predefined entity lists. The results do not yet prove robustness on real-world clinical text.
""" 

    with open(output_path, "w", encoding="utf-8") as file: 
        file.write(report) 
     
    print(report) 
    print(f"Summary saved to {output_path}") 

# FIXED: Added the double underscores required by Python's entry point check
if __name__ == "__main__": 
    create_summary()