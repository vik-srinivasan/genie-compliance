"""
Script 04: Run genie worksheet inference.
Uses worksheet template to structure LLM reasoning.
"""
from src.agents.genie_classifier import run_genie_inference

if __name__ == "__main__":
    run_genie_inference(
        "data/contracts_labeled.csv",
        "genie/worksheet_template.csv",
        "outputs/genie_inference.csv",
        "outputs/genie_metrics.json"
    )

