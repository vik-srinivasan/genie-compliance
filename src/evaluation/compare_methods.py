"""
Evaluation module.
Compares Baseline vs Gold, Genie vs Gold, and Genie vs Baseline.
"""
from typing import Dict
from src.utils.io import read_csv, write_json


def compute_comparison_metrics(predicted_csv: str, gold_label_col: str, predicted_col: str) -> Dict:
    """Compute metrics comparing predictions to gold labels."""
    rows = read_csv(predicted_csv)
    n = len(rows)
    
    tp = sum(1 for r in rows if r[predicted_col] == "safe" and r[gold_label_col] == "safe")
    tn = sum(1 for r in rows if r[predicted_col] == "unsafe" and r[gold_label_col] == "unsafe")
    fp = sum(1 for r in rows if r[predicted_col] == "safe" and r[gold_label_col] == "unsafe")
    fn = sum(1 for r in rows if r[predicted_col] == "unsafe" and r[gold_label_col] == "safe")
    
    acc = (tp + tn) / max(1, n)
    prec = tp / max(1, (tp + fp))
    rec = tp / max(1, (tp + fn))
    f1 = (2 * prec * rec) / max(1e-9, (prec + rec))
    
    return {
        "n_examples": n,
        "accuracy": round(acc, 3),
        "precision_safe": round(prec, 3),
        "recall_safe": round(rec, 3),
        "f1_safe": round(f1, 3),
        "confusion_matrix": {"tp": tp, "tn": tn, "fp": fp, "fn": fn}
    }


def compare_methods(
    baseline_csv: str,
    genie_csv: str,
    gold_label_col: str = "gold_label"
) -> Dict:
    """Compare baseline and genie methods against gold labels and each other."""
    # Baseline vs Gold
    baseline_vs_gold = compute_comparison_metrics(
        baseline_csv, gold_label_col, "agent_status"
    )
    
    # Genie vs Gold
    genie_vs_gold = compute_comparison_metrics(
        genie_csv, gold_label_col, "agent_status"
    )
    
    # Genie vs Baseline (treat baseline as "gold" for comparison)
    # Need to merge the two CSVs first
    baseline_rows = {r["id"]: r for r in read_csv(baseline_csv)}
    genie_rows = {r["id"]: r for r in read_csv(genie_csv)}
    
    # Create merged comparison
    merged = []
    for id_val in baseline_rows.keys():
        if id_val in genie_rows:
            merged.append({
                "id": id_val,
                "baseline_status": baseline_rows[id_val]["agent_status"],
                "genie_status": genie_rows[id_val]["agent_status"]
            })
    
    # Compute agreement metrics
    n_merged = len(merged)
    agree = sum(1 for r in merged if r["baseline_status"] == r["genie_status"])
    baseline_safe_genie_unsafe = sum(
        1 for r in merged 
        if r["baseline_status"] == "safe" and r["genie_status"] == "unsafe"
    )
    baseline_unsafe_genie_safe = sum(
        1 for r in merged 
        if r["baseline_status"] == "unsafe" and r["genie_status"] == "safe"
    )
    
    genie_vs_baseline = {
        "n_examples": n_merged,
        "agreement_rate": round(agree / max(1, n_merged), 3),
        "baseline_safe_genie_unsafe": baseline_safe_genie_unsafe,
        "baseline_unsafe_genie_safe": baseline_unsafe_genie_safe,
        "disagreement_rate": round((n_merged - agree) / max(1, n_merged), 3)
    }
    
    return {
        "baseline_vs_gold": baseline_vs_gold,
        "genie_vs_gold": genie_vs_gold,
        "genie_vs_baseline": genie_vs_baseline,
        "summary": {
            "baseline_accuracy": baseline_vs_gold["accuracy"],
            "genie_accuracy": genie_vs_gold["accuracy"],
            "accuracy_improvement": round(genie_vs_gold["accuracy"] - baseline_vs_gold["accuracy"], 3),
            "genie_f1": genie_vs_gold["f1_safe"],
            "baseline_f1": baseline_vs_gold["f1_safe"],
            "f1_improvement": round(genie_vs_gold["f1_safe"] - baseline_vs_gold["f1_safe"], 3)
        }
    }


def run(
    baseline_csv: str,
    genie_csv: str,
    output_json: str,
    gold_label_col: str = "gold_label"
):
    """Run evaluation comparison."""
    results = compare_methods(baseline_csv, genie_csv, gold_label_col)
    write_json(output_json, results)
    print(f"Evaluation complete. Saved to {output_json}")
    print(f"\nSummary:")
    print(f"  Baseline Accuracy: {results['summary']['baseline_accuracy']}")
    print(f"  Genie Accuracy: {results['summary']['genie_accuracy']}")
    print(f"  Accuracy Improvement: {results['summary']['accuracy_improvement']}")
    print(f"  Genie F1: {results['summary']['genie_f1']}")
    print(f"  Baseline F1: {results['summary']['baseline_f1']}")
    print(f"  F1 Improvement: {results['summary']['f1_improvement']}")


if __name__ == "__main__":
    run(
        "outputs/baseline_inference.csv",
        "outputs/genie_inference.csv",
        "outputs/evaluation_summary.json"
    )

