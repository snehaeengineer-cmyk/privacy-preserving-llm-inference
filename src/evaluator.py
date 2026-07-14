import ast
import pandas as pd


def evaluate_privacy(results_path, ground_truth_path, output_path):
    """
    Evaluate PII detection and masking leakage against ground truth labels.
    """

    results_df = pd.read_csv(results_path)
    gt_df = pd.read_csv(ground_truth_path)

    evaluation_rows = []

    for prompt_id in results_df["prompt_id"].unique():
        result_row = results_df[results_df["prompt_id"] == prompt_id].iloc[0]

        masked_prompt = str(result_row["masked_prompt"])

        ground_truth_entities = gt_df[gt_df["prompt_id"] == prompt_id]["entity_text"].tolist()

        try:
            detected_entities = ast.literal_eval(result_row["detected_entities"])
        except Exception:
            detected_entities = []

        detected_texts = [entity["text"] for entity in detected_entities]

        correctly_detected = []
        missed = []
        leaked = []

        for gt_entity in ground_truth_entities:
            if gt_entity in detected_texts:
                correctly_detected.append(gt_entity)
            else:
                missed.append(gt_entity)

            if gt_entity in masked_prompt:
                leaked.append(gt_entity)

        total_ground_truth = len(ground_truth_entities)
        total_detected_correctly = len(correctly_detected)
        total_leaked = len(leaked)

        if total_ground_truth > 0:
            pii_recall = total_detected_correctly / total_ground_truth
            leakage_rate = total_leaked / total_ground_truth
        else:
            pii_recall = 0
            leakage_rate = 0

        evaluation_rows.append({
            "prompt_id": prompt_id,
            "ground_truth_count": total_ground_truth,
            "correctly_detected_count": total_detected_correctly,
            "pii_recall": round(pii_recall, 3),
            "leaked_pii_count": total_leaked,
            "leakage_rate": round(leakage_rate, 3),
            "correctly_detected": str(correctly_detected),
            "missed_pii": str(missed),
            "leaked_pii": str(leaked)
        })

    evaluation_df = pd.DataFrame(evaluation_rows)
    evaluation_df.to_csv(output_path, index=False, encoding="utf-8")

    average_recall = evaluation_df["pii_recall"].mean()
    average_leakage = evaluation_df["leakage_rate"].mean()

    print("\nPrivacy evaluation complete.")
    print("Average PII recall:", round(average_recall, 3))
    print("Average leakage rate:", round(average_leakage, 3))
    print(f"Saved evaluation to {output_path}")


if __name__ == "__main__":
    evaluate_privacy(
        results_path="outputs/results.csv",
        ground_truth_path="data/ground_truth_pii.csv",
        output_path="outputs/privacy_evaluation.csv"
    )