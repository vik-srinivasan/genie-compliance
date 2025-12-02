"""
Genie worksheet-based classifier.
Loads worksheet template and uses it to structure LLM reasoning.
"""
import os
import openai
import csv
from typing import List, Dict, Any
from dotenv import load_dotenv
from src.utils.io import read_csv, write_csv, write_json
from src.pipeline.inference_metrics import compute

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Use a smaller OpenAI model by default; override via OPENAI_MODEL if desired.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


WORKSHEET_TEMPLATE_PATH = "genie/worksheet_template.csv"


def load_worksheet_template(path: str) -> List[Dict[str, Any]]:
    """Load the genie worksheet template CSV."""
    with open(path, "r", newline="") as f:
        return list(csv.DictReader(f))


def build_worksheet_prompt(worksheet_rows: List[Dict], contract_code: str) -> str:
    """Build a structured prompt from the worksheet template and contract code."""
    prompt_parts = [
        "You are analyzing a Solidity contract for safety using a structured worksheet approach.",
        "",
        "CONTRACT CODE TO ANALYZE:",
        "```solidity",
        contract_code,
        "```",
        "",
        "SAFETY CHECK WORKSHEET:",
        "",
        "1. BALANCE SAFETY CHECK",
        "   - Check if balance is verified before transfer using require(balance >= amount) pattern",
        "   - Identify line numbers or code snippets showing the balance check",
        "",
        "2. ARITHMETIC SAFETY CHECK",
        "   - Check for arithmetic overflow/underflow risks in calculations",
        "   - Identify evidence of arithmetic safety issues or protections",
        "",
        "3. ACCESS CONTROL CHECK",
        "   - Check for proper access control (e.g., only owner can call, proper modifiers)",
        "   - Identify evidence of access control mechanisms or lack thereof",
        "",
        "4. INPUT VALIDATION CHECK",
        "   - Check if inputs are validated (non-zero addresses, positive amounts, etc.)",
        "   - Identify evidence of input validation or missing validation",
        "",
        "5. STATE CONSISTENCY CHECK",
        "   - Check if state updates are consistent (balances updated correctly, no double-spending)",
        "   - Identify evidence of state consistency or inconsistency issues",
        "",
        "OUTPUT FORMAT:",
        "FIRST, you MUST output a single line exactly in one of these forms:",
        "DECISION: SAFE",
        "or",
        "DECISION: UNSAFE",
        "",
        "Immediately after that, provide your analysis in the following structured format:",
        "BALANCE_CHECK: [true/false] - [evidence or explanation]",
        "ARITHMETIC_SAFETY: [true/false] - [evidence or explanation]",
        "ACCESS_CONTROL: [true/false] - [evidence or explanation]",
        "INPUT_VALIDATION: [true/false] - [evidence or explanation]",
        "STATE_CONSISTENCY: [true/false] - [evidence or explanation]",
        "",
        "REASONING: [Detailed explanation of your analysis]",
        "",
        "Begin your analysis:"
    ]
    
    return "\n".join(prompt_parts)


def parse_genie_response(response: str) -> Dict:
    """Parse the structured response from the LLM."""
    result = {
        "status": "unsafe",
        "reasoning": "",
        "evidence": {},
        "evidence_summary": ""
    }
    
    lines = response.split("\n")
    current_section = None
    reasoning_lines = []
    decision_found = False

    # 1) Try to read first non-empty line as explicit DECISION.
    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue
        upper = line.upper()
        if upper.startswith("DECISION:"):
            decision_text = upper.split(":", 1)[1].strip()
            if "UNSAFE" in decision_text:
                result["status"] = "unsafe"
            elif "SAFE" in decision_text:
                result["status"] = "safe"
            decision_found = True
            # Reasoning starts after the decision line
            lines = lines[idx + 1 :]
            break

    # 2) Parse remaining lines for worksheet sections and reasoning.
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse structured fields
        if line.startswith("BALANCE_CHECK:"):
            parts = line.split(":", 1)[1].strip().split(" - ", 1)
            result["evidence"]["balance_check"] = {
                "has_check": "true" in parts[0].lower() if parts else False,
                "evidence": parts[1] if len(parts) > 1 else ""
            }
        elif line.startswith("ARITHMETIC_SAFETY:"):
            parts = line.split(":", 1)[1].strip().split(" - ", 1)
            result["evidence"]["arithmetic_safety"] = {
                "safe": "true" in parts[0].lower() if parts else False,
                "evidence": parts[1] if len(parts) > 1 else ""
            }
        elif line.startswith("ACCESS_CONTROL:"):
            parts = line.split(":", 1)[1].strip().split(" - ", 1)
            result["evidence"]["access_control"] = {
                "has_control": "true" in parts[0].lower() if parts else False,
                "evidence": parts[1] if len(parts) > 1 else ""
            }
        elif line.startswith("INPUT_VALIDATION:"):
            parts = line.split(":", 1)[1].strip().split(" - ", 1)
            result["evidence"]["input_validation"] = {
                "has_validation": "true" in parts[0].lower() if parts else False,
                "evidence": parts[1] if len(parts) > 1 else ""
            }
        elif line.startswith("STATE_CONSISTENCY:"):
            parts = line.split(":", 1)[1].strip().split(" - ", 1)
            result["evidence"]["state_consistency"] = {
                "consistent": "true" in parts[0].lower() if parts else False,
                "evidence": parts[1] if len(parts) > 1 else ""
            }
        elif line.startswith("REASONING:"):
            current_section = "reasoning"
            reasoning_lines.append(line.split(":", 1)[1].strip() if ":" in line else "")
        elif line.startswith("DECISION:"):
            decision_text = line.split(":", 1)[1].strip().upper() if ":" in line else line.upper()
            result["status"] = "safe" if "SAFE" in decision_text else "unsafe"
            decision_found = True
        elif current_section == "reasoning":
            reasoning_lines.append(line)
    
    result["reasoning"] = " ".join(reasoning_lines) if reasoning_lines else response
    result["evidence_summary"] = "; ".join([
        f"{k}: {v.get('evidence', '')[:50]}" 
        for k, v in result["evidence"].items() 
        if isinstance(v, dict) and "evidence" in v
    ])
    
    # If no structured parsing worked, try to extract decision from response
    if not decision_found:
        response_upper = response.upper()
        if "SAFE" in response_upper and "UNSAFE" not in response_upper:
            result["status"] = "safe"
        elif "UNSAFE" in response_upper:
            result["status"] = "unsafe"
        result["reasoning"] = response
    
    return result


def classify_with_genie(worksheet_rows: List[Dict], code: str) -> Dict:
    """Classify a contract using genie worksheet approach."""
    try:
        prompt = build_worksheet_prompt(worksheet_rows, code)
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1000
        )
        response_text = response.choices[0].message.content.strip()
        parsed = parse_genie_response(response_text)
        return parsed
    except Exception as e:
        print(f"Genie classification error: {e}")
        return {
            "status": "unsafe",
            "reasoning": f"Error during classification: {e}",
            "evidence": {},
            "evidence_summary": ""
        }


def run_genie_inference(input_csv: str, worksheet_path: str, output_csv: str, metrics_json: str):
    """Run genie worksheet-based inference on labeled contracts."""
    worksheet_rows = load_worksheet_template(worksheet_path)
    rows = read_csv(input_csv)
    results = []
    
    for i, row in enumerate(rows):
        print(f"Genie inference {i+1}/{len(rows)}...")
        code = row["code"]
        result = classify_with_genie(worksheet_rows, code)
        results.append({
            "id": row["id"],
            "gold_label": row["final_label"],
            "agent_status": result["status"],
            "reasoning": result["reasoning"],
            "evidence_summary": result["evidence_summary"]
        })
    
    write_csv(
        output_csv,
        results,
        fieldnames=["id", "gold_label", "agent_status", "reasoning", "evidence_summary"]
    )
    
    metrics = compute(output_csv)
    write_json(metrics_json, metrics)
    
    print(f"Genie inference complete. Saved to {output_csv}")
    print(f"Metrics saved to {metrics_json}")


if __name__ == "__main__":
    run_genie_inference(
        "data/contracts_labeled.csv",
        WORKSHEET_TEMPLATE_PATH,
        "outputs/genie_inference.csv",
        "outputs/genie_metrics.json"
    )

