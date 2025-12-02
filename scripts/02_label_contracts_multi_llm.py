"""
Script 02: Label contracts with multi-LLM pipeline.
Sends contracts to GPT, Claude, and Gemini for labeling.
"""
from src.pipeline.llm_labeler import run

if __name__ == "__main__":
    run(
        "data/contracts_raw.csv",
        "data/contracts_labeled.csv",
        "outputs/labeling_metrics.json"
    )

