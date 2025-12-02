"""
Script 03: Run baseline inference.
Single-shot SAFE/UNSAFE classification without worksheets.
"""
from src.agents.baseline_classifier import run_baseline_inference

if __name__ == "__main__":
    run_baseline_inference(
        "data/contracts_labeled.csv",
        "outputs/baseline_inference.csv",
        "outputs/baseline_metrics.json"
    )

