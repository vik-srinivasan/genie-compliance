from typing import Dict
from src.utils.io import read_csv, write_json

def compute(inference_csv: str) -> Dict:
    rows = read_csv(inference_csv)
    n = len(rows)
    tp = sum(1 for r in rows if r["agent_status"] == "safe" and r["gold_label"] == "safe")
    tn = sum(1 for r in rows if r["agent_status"] == "unsafe" and r["gold_label"] == "unsafe")
    fp = sum(1 for r in rows if r["agent_status"] == "safe" and r["gold_label"] == "unsafe")
    fn = sum(1 for r in rows if r["agent_status"] == "unsafe" and r["gold_label"] == "safe")

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
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn}
    }

def run(inference_csv: str, out_json: str):
    write_json(out_json, compute(inference_csv))
