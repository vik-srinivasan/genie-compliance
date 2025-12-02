"""
Multi-LLM labeling pipeline.
Sends contracts to GPT (simulating multi-LLM with different prompts/temperatures).
"""
import os
import openai
from typing import List, Dict
from dotenv import load_dotenv
from src.utils.io import read_csv, write_csv, write_json

load_dotenv()

# Initialize API client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Use a smaller OpenAI model by default; override via OPENAI_MODEL if desired.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

LABELING_PROMPT = """Analyze this Solidity transfer function and classify it as SAFE or UNSAFE.

CRITICAL: A function is SAFE ONLY if it has ALL of the following:
1. Checks balance before transferring (require(balance >= amount) or similar)
2. Proper access control (if needed)
3. Input validation (if needed)
4. State consistency maintained

A function is UNSAFE if it is MISSING the balance check (require statement checking balance >= amount before transfer).

Code:
{code}

IMPORTANT: If you don't see a require() statement checking balance before the transfer, it is UNSAFE.
Respond with ONLY one word: SAFE or UNSAFE"""


def label_with_gpt(code: str) -> str:
    """Label contract using GPT."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "user", "content": LABELING_PROMPT.format(code=code)}
            ],
            temperature=0.0,
            max_tokens=10
        )
        label = response.choices[0].message.content.strip().upper()
        # Check for UNSAFE first (more specific), then SAFE, default to unsafe
        if "UNSAFE" in label:
            return "unsafe"
        elif "SAFE" in label:
            return "safe"
        else:
            # Default to unsafe if unclear
            return "unsafe"
    except Exception as e:
        print(f"GPT labeling error: {e}")
        return "unsafe"  # Default to unsafe on error


def label_with_claude(code: str) -> str:
    """Label contract using GPT (simulating Claude with different prompt)."""
    try:
        # Use slightly different prompt to simulate different model
        prompt = LABELING_PROMPT.format(code=code) + "\n\nConsider the security implications carefully."
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Slight variation
            max_tokens=10
        )
        label = response.choices[0].message.content.strip().upper()
        # Check for UNSAFE first (more specific), then SAFE, default to unsafe
        if "UNSAFE" in label:
            return "unsafe"
        elif "SAFE" in label:
            return "safe"
        else:
            # Default to unsafe if unclear
            return "unsafe"
    except Exception as e:
        print(f"Claude (GPT) labeling error: {e}")
        return "unsafe"  # Default to unsafe on error


def label_with_gemini(code: str) -> str:
    """Label contract using GPT (simulating Gemini with different prompt)."""
    try:
        # Use slightly different prompt to simulate different model
        prompt = "Classify this Solidity transfer function as SAFE or UNSAFE:\n\n" + code + "\n\n" + \
                 "CRITICAL: If the function is MISSING a require() statement checking balance before transfer, it is UNSAFE.\n" + \
                 "SAFE only if balance check exists. UNSAFE if balance check is missing.\n" + \
                 "Respond with ONLY one word: SAFE or UNSAFE"
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Slight variation
            max_tokens=10
        )
        label = response.choices[0].message.content.strip().upper()
        # Check for UNSAFE first (more specific), then SAFE, default to unsafe
        if "UNSAFE" in label:
            return "unsafe"
        elif "SAFE" in label:
            return "safe"
        else:
            # Default to unsafe if unclear
            return "unsafe"
    except Exception as e:
        print(f"Gemini (GPT) labeling error: {e}")
        return "unsafe"  # Default to unsafe on error


def compute_confidence(gpt_label: str, claude_label: str, gemini_label: str) -> float:
    """Compute confidence based on agreement."""
    labels = [gpt_label, claude_label, gemini_label]
    agreement_count = max(labels.count("safe"), labels.count("unsafe"))
    return round(agreement_count / 3.0, 2)


def label_batch(rows: List[Dict]) -> List[Dict]:
    """Label all contracts using multi-LLM pipeline."""
    labeled = []
    
    for i, row in enumerate(rows):
        print(f"Labeling contract {i+1}/{len(rows)}...")
        code = row["code"]
        
        gpt_label = label_with_gpt(code)
        claude_label = label_with_claude(code)
        gemini_label = label_with_gemini(code)
        
        # Agreement logic: unanimous -> gold label; otherwise needs_review = true
        all_agree = (gpt_label == claude_label == gemini_label)
        final_label = gpt_label if all_agree else gpt_label  # Use GPT as tiebreaker
        confidence = compute_confidence(gpt_label, claude_label, gemini_label)
        needs_review = not all_agree
        
        labeled.append({
            "id": row["id"],
            "code": code,
            "gpt_label": gpt_label,
            "claude_label": claude_label,
            "gemini_label": gemini_label,
            "final_label": final_label,
            "confidence": str(confidence),
            "needs_review": str(needs_review).lower()
        })
    
    return labeled


def compute_labeling_metrics(labeled: List[Dict]) -> Dict:
    """Compute metrics for labeling pipeline."""
    n = len(labeled)
    agree_count = sum(1 for r in labeled if r["needs_review"] == "false")
    avg_confidence = sum(float(r["confidence"]) for r in labeled) / max(1, n)
    
    return {
        "n_contracts": n,
        "agreement_rate": round(agree_count / max(1, n), 3),
        "average_confidence": round(avg_confidence, 3),
        "needs_review_count": n - agree_count
    }


def run(input_csv: str, output_csv: str, metrics_json: str):
    """Run multi-LLM labeling pipeline."""
    rows = read_csv(input_csv)
    labeled = label_batch(rows)
    
    write_csv(
        output_csv,
        labeled,
        fieldnames=["id", "code", "gpt_label", "claude_label", "gemini_label", 
                   "final_label", "confidence", "needs_review"]
    )
    
    metrics = compute_labeling_metrics(labeled)
    write_json(metrics_json, metrics)
    
    print(f"Labeling complete. Saved to {output_csv}")
    print(f"Metrics saved to {metrics_json}")


if __name__ == "__main__":
    run(
        "data/contracts_raw.csv",
        "data/contracts_labeled.csv",
        "outputs/labeling_metrics.json"
    )

