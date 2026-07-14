import ast
import os
import pandas as pd
import matplotlib.pyplot as plt 

def safe_parse(value):
    """ Safely parse stringified Python lists/dicts from CSV cells. """
    try:
        return ast.literal_eval(value)
    except Exception:
        return [] 

def create_output_folder():
    """ Create outputs/charts folder if it does not exist. """
    os.makedirs("outputs/charts", exist_ok=True) 

def plot_entity_type_counts(results_df):
    """ Create a bar chart showing how many entities were detected per entity type. """ 
    entity_counts = {} 
     
    for _, row in results_df.iterrows(): 
        detected_entities = safe_parse(row["detected_entities"]) 
     
        for entity in detected_entities: 
            entity_type = entity.get("type", "UNKNOWN") 
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1 
     
    entity_counts_df = pd.DataFrame( 
        list(entity_counts.items()), 
        columns=["entity_type", "count"] 
    ).sort_values(by="count", ascending=True) 
     
    plt.figure(figsize=(10, 6)) 
    plt.barh(entity_counts_df["entity_type"], entity_counts_df["count"]) 
    plt.xlabel("Count") 
    plt.ylabel("Entity Type") 
    plt.title("Detected Entity Type Counts") 
    plt.tight_layout() 
    plt.savefig("outputs/charts/entity_type_counts.png", dpi=300) 
    plt.close() 
 
def plot_policy_decisions(results_df):
    """ Create a bar chart showing PASS/WARN/BLOCK policy decisions. """ 
    if "policy_decision" not in results_df.columns: 
        print("No policy_decision column found.") 
        return 
     
    counts = results_df["policy_decision"].value_counts() 
     
    plt.figure(figsize=(7, 5)) 
    plt.bar(counts.index, counts.values) 
    plt.xlabel("Policy Decision") 
    plt.ylabel("Number of Prompts") 
    plt.title("Policy Decision Counts") 
    plt.tight_layout() 
    plt.savefig("outputs/charts/policy_decision_counts.png", dpi=300) 
    plt.close() 
 
def plot_quasi_identifier_risk(results_df):
    """ Create a bar chart showing quasi-identifier risk levels. """ 
    if "quasi_identifier_risk_level" not in results_df.columns: 
        print("No quasi_identifier_risk_level column found.") 
        return 
     
    counts = results_df["quasi_identifier_risk_level"].value_counts() 
     
    plt.figure(figsize=(7, 5)) 
    plt.bar(counts.index, counts.values) 
    plt.xlabel("Risk Level") 
    plt.ylabel("Number of Prompts") 
    plt.title("Quasi-Identifier Risk Counts") 
    plt.tight_layout() 
    plt.savefig("outputs/charts/quasi_identifier_risk_counts.png", dpi=300) 
    plt.close() 
 
def plot_utility_scores():
    """ Create a bar chart for average utility score by condition. """ 
    utility_path = "outputs/utility_evaluation_template.csv" 
     
    if not os.path.exists(utility_path) or os.path.getsize(utility_path) == 0: 
        print("Utility evaluation file missing or empty. Skipping utility chart.") 
        return 
     
    utility_df = pd.read_csv(utility_path) 
     
    if "overall_score" not in utility_df.columns: 
        print("No overall_score column found. Skipping utility chart.") 
        return 
     
    utility_df["overall_score"] = pd.to_numeric( 
        utility_df["overall_score"], 
        errors="coerce" 
    ) 
     
    utility_df = utility_df.dropna(subset=["overall_score"]) 
     
    if len(utility_df) == 0: 
        print("No utility scores filled. Skipping utility chart.") 
        return 
     
    avg_scores = ( 
        utility_df 
        .groupby("condition")["overall_score"] 
        .mean() 
        .sort_values(ascending=True) 
    ) 
     
    plt.figure(figsize=(8, 5)) 
    plt.barh(avg_scores.index, avg_scores.values) 
    plt.xlabel("Average Utility Score") 
    plt.ylabel("Condition") 
    plt.title("Average Utility Score by Condition") 
    plt.xlim(0, 5) 
    plt.tight_layout() 
    plt.savefig("outputs/charts/utility_score_by_condition.png", dpi=300) 
    plt.close() 
 
def main():
    """ Generate all charts from project outputs. """ 
    create_output_folder() 
     
    results_path = "outputs/results.csv" 
     
    if not os.path.exists(results_path): 
        print("outputs/results.csv not found. Run python src/main.py first.") 
        return 
     
    results_df = pd.read_csv(results_path) 
     
    plot_entity_type_counts(results_df) 
    plot_policy_decisions(results_df) 
    plot_quasi_identifier_risk(results_df) 
    plot_utility_scores() 
     
    print("Charts created successfully.") 
    print("Check the folder: outputs/charts/") 
 
if __name__ == "__main__":
    main()