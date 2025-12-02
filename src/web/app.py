"""
Flask web application for contract safety chatbot.
"""
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from src.agents.genie_classifier import load_worksheet_template, classify_with_genie
import openai

load_dotenv()

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
CORS(app)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Load worksheet template once at startup
WORKSHEET_TEMPLATE_PATH = "genie/worksheet_template.csv"
worksheet_rows = load_worksheet_template(WORKSHEET_TEMPLATE_PATH)


@app.route("/")
def index():
    """Serve the main chat interface."""
    return render_template("index.html")


@app.route("/api/classify", methods=["POST"])
def classify_contract():
    """Classify a contract as safe or unsafe using genie agent."""
    try:
        data = request.json
        contract_code = data.get("code", "").strip()
        
        if not contract_code:
            return jsonify({"error": "No contract code provided"}), 400
        
        # Use genie classifier
        result = classify_with_genie(worksheet_rows, contract_code)
        
        return jsonify({
            "status": result["status"],
            "reasoning": result["reasoning"],
            "evidence_summary": result["evidence_summary"],
            "evidence": result.get("evidence", {})
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint for helping fix unsafe contracts."""
    try:
        data = request.json
        user_message = data.get("message", "").strip()
        contract_code = data.get("contract_code", "").strip()
        classification_status = data.get("status", "unknown")
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        if not contract_code:
            return jsonify({"error": "No contract code provided"}), 400
        
        # Build context-aware prompt
        system_prompt = """You are a helpful Solidity security expert assistant. Your role is to help developers fix unsafe smart contracts.
        
When a contract is marked as UNSAFE, help the user understand the issues and provide specific, actionable fixes.
When a contract is marked as SAFE, you can still help with improvements or answer questions about the code.
        
Be concise, practical, and provide code examples when relevant."""
        
        user_prompt = f"""Contract Status: {classification_status.upper()}

Contract Code:
```solidity
{contract_code}
```

User Question: {user_message}

Please provide helpful guidance to fix or improve this contract."""
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        assistant_message = response.choices[0].message.content.strip()
        
        return jsonify({
            "message": assistant_message
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)

