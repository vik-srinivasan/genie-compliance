"""
Script 05: Run evaluation.
Compares Baseline vs Gold, Genie vs Gold, and Genie vs Baseline.
"""
from src.evaluation.compare_methods import run

if __name__ == "__main__":
    run(
        "outputs/baseline_inference.csv",
        "outputs/genie_inference.csv",
        "outputs/evaluation_summary.json"
    )

