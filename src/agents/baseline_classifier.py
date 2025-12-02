"""
Baseline LLM classifier.
Single-shot SAFE/UNSAFE classification without worksheets.
"""
import os
import openai
from typing import List, Dict
from dotenv import load_dotenv
from src.utils.io import read_csv, write_csv, write_json
from src.pipeline.inference_metrics import compute

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Use a smaller OpenAI model by default; override via OPENAI_MODEL if desired.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


BASELINE_PROMPT = """You are a security analyst for Solidity ERC20-style transfer functions.
Classify the function as SAFE or UNSAFE, then explain your reasoning.

A function is SAFE ONLY if ALL of the following are true:
- It checks the sender's balance BEFORE transferring (e.g., require(balance >= amount)).
- It keeps token balances consistent (no double-spend, no obvious bugs).

Treat the function as UNSAFE if:
- There is NO require-like balance check before updating balances, OR
- The balance check is clearly incorrect or can be bypassed.

Code to analyze:
```solidity
{code}
```

CRITICAL: Your first line MUST be exactly:
LABEL: SAFE
or
LABEL: UNSAFE

Then on the next line, write:
EXPLANATION: <short explanation of why>.
Do not put any other content before LABEL:.
"""


def classify(code: str) -> Dict:
    """Classify a contract as safe or unsafe using baseline LLM."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "user", "content": BASELINE_PROMPT.format(code=code)}
            ],
            temperature=0.0,
            max_tokens=200
        )
        raw = response.choices[0].message.content.strip()
        lines = [l for l in raw.splitlines() if l.strip()]

        # Default values
        status = "unsafe"
        explanation = raw

        if lines:
            first = lines[0].strip()
            upper_first = first.upper()
            # Expected format: LABEL: SAFE or LABEL: UNSAFE
            if upper_first.startswith("LABEL:"):
                label_token = upper_first.split(":", 1)[1].strip()
            else:
                # Fallback: first token on the line
                label_token = upper_first.split()[0]

            if "UNSAFE" in label_token:
                status = "unsafe"
            elif "SAFE" in label_token:
                status = "safe"

            # Explanation: prefer second line starting with EXPLANATION:
            if len(lines) > 1:
                second = lines[1].strip()
                if second.upper().startswith("EXPLANATION:"):
                    explanation = second.split(":", 1)[1].strip() or raw
                else:
                    explanation = "\n".join(lines[1:]).strip() or raw

        return {
            "status": status,
            "explanation": explanation
        }
    except Exception as e:
        print(f"Baseline classification error: {e}")
        return {
            "status": "unsafe",
            "explanation": f"Error during classification: {e}"
        }


def run_baseline_inference(input_csv: str, output_csv: str, metrics_json: str):
    """Run baseline inference on labeled contracts."""
    rows = read_csv(input_csv)
    results = []
    
    for i, row in enumerate(rows):
        print(f"Baseline inference {i+1}/{len(rows)}...")
        code = row["code"]
        result = classify(code)
        results.append({
            "id": row["id"],
            "gold_label": row["final_label"],
            "agent_status": result["status"],
            "explanation": result["explanation"]
        })
    
    write_csv(
        output_csv,
        results,
        fieldnames=["id", "gold_label", "agent_status", "explanation"]
    )
    
    metrics = compute(output_csv)
    write_json(metrics_json, metrics)
    
    print(f"Baseline inference complete. Saved to {output_csv}")
    print(f"Metrics saved to {metrics_json}")


if __name__ == "__main__":
    run_baseline_inference(
        "data/contracts_labeled.csv",
        "outputs/baseline_inference.csv",
        "outputs/baseline_metrics.json"
    )

