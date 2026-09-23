import os
import json
import requests
import math

PORT = int(os.environ.get("PORT", "8000"))
BASE_URL = f"http://127.0.0.1:{PORT}/api/v1/test-audio"

def main():
    print("Fetching test audio samples...")
    try:
        res = requests.get(BASE_URL)
        res.raise_for_status()
    except Exception as e:
        print(f"Error fetching samples (is backend running?): {e}")
        return
        
    samples = res.json().get("samples", [])
    if not samples:
        print("No samples found.")
        return
        
    print(f"Found {len(samples)} samples. Beginning evaluation...")
    
    reports = []
    tp, tn, fp, fn = 0, 0, 0, 0
    
    for s in samples:
        sample_id = s["id"]
        print(f"Analyzing {sample_id}...", end="", flush=True)
        try:
            analyze_url = f"{BASE_URL}/{sample_id}/analyze"
            r = requests.post(analyze_url, timeout=60)
            r.raise_for_status()
            data = r.json()
            
            ground_truth = data["test_sample"]["ground_truth"] # GENUINE or DEEPFAKE
            pred = data["deepfake"]["prediction"] # REAL or FAKE
            
            reports.append({
                "sample_id": sample_id,
                "ground_truth": ground_truth,
                "prediction": pred,
                "fake_probability": data["deepfake"]["fake_probability"]
            })
            
            print(f" -> GT: {ground_truth}, Pred: {pred}")
            
            # Bonafide (GENUINE) = Negative for deepfake detection
            # Spoof (DEEPFAKE) = Positive for deepfake detection
            is_actual_fake = (ground_truth == "DEEPFAKE")
            is_pred_fake = (pred == "FAKE")
            
            if is_actual_fake and is_pred_fake: tp += 1
            elif is_actual_fake and not is_pred_fake: fn += 1
            elif not is_actual_fake and is_pred_fake: fp += 1
            elif not is_actual_fake and not is_pred_fake: tn += 1
            
        except Exception as e:
            print(f" Error: {e}")
            
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    report_data = {
        "metrics": {
            "total_evaluated": total,
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        },
        "details": reports
    }
    
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    json_path = os.path.join(reports_dir, "test_audio_evaluation.json")
    md_path = os.path.join(reports_dir, "test_audio_evaluation.md")
    
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=2)
        
    with open(md_path, "w") as f:
        f.write("# AASIST Test Audio Evaluation Report\n\n")
        f.write("## Metrics\n")
        f.write(f"- Total Evaluated: {total}\n")
        f.write(f"- True Positives: {tp}\n")
        f.write(f"- True Negatives: {tn}\n")
        f.write(f"- False Positives: {fp}\n")
        f.write(f"- False Negatives: {fn}\n")
        f.write(f"- Accuracy: {accuracy:.2%}\n")
        f.write(f"- Precision: {precision:.2%}\n")
        f.write(f"- Recall: {recall:.2%}\n")
        f.write(f"- F1 Score: {f1:.4f}\n\n")
        f.write("## Details\n")
        for r in reports:
            f.write(f"- **{r[
sample_id]}** - GT: {r[ground_truth]} | Pred: {r[prediction]} (Fake Prob: {r[fake_probability]:.2%})\n")
    
    print("\nEvaluation complete. Reports saved to reports/ directory.")

if __name__ == "__main__":
    main()

