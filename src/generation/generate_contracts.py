"""
Contract generation module.
Generates 250 Solidity-like contract snippets using GPT.
"""
import os
import openai
from typing import List, Dict
from dotenv import load_dotenv
from src.utils.io import write_csv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Use a smaller OpenAI model by default; override via OPENAI_MODEL if desired.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


SYSTEM_PROMPT = """You are a Solidity contract generator. Generate realistic ERC20-like transfer function snippets.
Include variations in:
- Variable names (balance, ledger, balances, etc.)
- Order of operations
- Comments
- Arithmetic patterns
- Access control checks
- Missing/incorrect balance checks
- Missing validation
- State inconsistency issues

Generate ONLY the function code, not a full contract. Keep it concise (5-15 lines)."""

USER_PROMPT_TEMPLATE = """Generate a Solidity transfer function snippet. 
Make it {variation_type}. 
Return ONLY the code, no explanations."""

VARIATION_TYPES = [
    "safe with proper balance check",
    "safe with proper balance check and access control",
    "unsafe missing balance check",
    "unsafe with incorrect balance check",
    "unsafe with arithmetic overflow risk",
    "unsafe with state inconsistency",
    "safe with input validation",
    "unsafe missing input validation",
    "safe with proper checks and comments",
    "unsafe with wrong variable in check",
] * 25  # 10 types * 25 = 250 contracts


def generate_contract(variation_type: str, contract_id: int) -> str:
    """Generate a single contract snippet using GPT."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(variation_type=variation_type)}
            ],
            temperature=0.8,
            max_tokens=300
        )
        code = response.choices[0].message.content.strip()
        # Remove markdown code blocks if present
        if code.startswith("```"):
            lines = code.split("\n")
            code = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        return code
    except Exception as e:
        print(f"Error generating contract {contract_id}: {e}")
        # Fallback to a simple template
        return f"// Contract {contract_id}\nfunction transfer(address to, uint256 amount) public {{\n    // Generated code\n}}"


def generate_all_contracts(output_path: str = "data/contracts_raw.csv"):
    """Generate 250 contract snippets and save to CSV."""
    print("Generating 250 contract snippets...")
    contracts = []
    
    for i, variation in enumerate(VARIATION_TYPES):
        print(f"Generating contract {i+1}/250...")
        code = generate_contract(variation, i)
        contracts.append({
            "id": str(i),
            "code": code
        })
    
    write_csv(output_path, contracts, fieldnames=["id", "code"])
    print(f"Generated {len(contracts)} contracts. Saved to {output_path}")


if __name__ == "__main__":
    generate_all_contracts()

