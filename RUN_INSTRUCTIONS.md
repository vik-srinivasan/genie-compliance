# Step-by-Step Execution Guide

## Prerequisites

1. **Python Environment Setup**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Key**
   Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```
   Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Execution Steps

### Step 1: Generate Contracts
Generate 250 Solidity contract snippets using GPT.

```bash
python -m scripts.01_generate_contracts
```

**Expected Output:**
- `data/contracts_raw.csv` - Contains 250 contract snippets with columns: `id`, `code`
- Console output showing progress for each contract generation

**Time Estimate:** ~10-15 minutes (depending on API rate limits)

---

### Step 2: Label Contracts with Multi-LLM Pipeline
Label all contracts using multi-LLM with different prompts.

```bash
python -m scripts.02_label_contracts_multi_llm
```

**Expected Output:**
- `data/contracts_labeled.csv` - Contains labeled contracts with columns:
  - `id`, `code`, `gpt_label`, `claude_label`, `gemini_label`, `final_label`, `confidence`, `needs_review`
- `outputs/labeling_metrics.json` - Metrics about labeling agreement and confidence

**Time Estimate:** ~15-20 minutes (3 API calls per contract × 250 contracts)

---

### Step 3: Run Baseline Inference
Run baseline LLM classification (single-shot, no worksheets).

```bash
python -m scripts.03_run_baseline_inference
```

**Expected Output:**
- `outputs/baseline_inference.csv` - Baseline predictions with columns:
  - `id`, `gold_label`, `agent_status`, `explanation`
- `outputs/baseline_metrics.json` - Accuracy, precision, recall, F1 metrics

**Time Estimate:** ~5-8 minutes (1 API call per contract × 250 contracts)

---

### Step 4: Run Genie Worksheet Inference
Run genie worksheet-based classification using structured reasoning.

```bash
python -m scripts.04_run_genie_inference
```

**Expected Output:**
- `outputs/genie_inference.csv` - Genie predictions with columns:
  - `id`, `gold_label`, `agent_status`, `reasoning`, `evidence_summary`
- `outputs/genie_metrics.json` - Accuracy, precision, recall, F1 metrics

**Time Estimate:** ~10-15 minutes (1 API call per contract × 250 contracts, longer prompts)

---

### Step 5: Run Evaluation
Compare all methods and generate evaluation summary.

```bash
python -m scripts.05_run_evaluation
```

**Expected Output:**
- `outputs/evaluation_summary.json` - Comprehensive comparison with:
  - `baseline_vs_gold` - Baseline performance metrics
  - `genie_vs_gold` - Genie performance metrics
  - `genie_vs_baseline` - Agreement/disagreement between methods
  - `summary` - Key improvements and differences

**Time Estimate:** < 1 minute (no API calls, just computation)

---

## Quick Run (All Steps)

To run the entire pipeline in sequence:

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run all steps
python -m scripts.01_generate_contracts
python -m scripts.02_label_contracts_multi_llm
python -m scripts.03_run_baseline_inference
python -m scripts.04_run_genie_inference
python -m scripts.05_run_evaluation
```

**Total Time Estimate:** ~40-60 minutes

---

## Output Files Summary

### Data Files
- `data/contracts_raw.csv` - Generated contract snippets
- `data/contracts_labeled.csv` - Labeled contracts with gold labels

### Output Files
- `outputs/labeling_metrics.json` - Multi-LLM labeling statistics
- `outputs/baseline_inference.csv` - Baseline predictions
- `outputs/baseline_metrics.json` - Baseline performance metrics
- `outputs/genie_inference.csv` - Genie worksheet predictions
- `outputs/genie_metrics.json` - Genie performance metrics
- `outputs/evaluation_summary.json` - Final comparison summary

---

## Troubleshooting

### API Key Issues
- Ensure `.env` file exists in project root
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has sufficient credits/quota

### Import Errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version (3.8+ required)

### File Not Found Errors
- Ensure you're running scripts from project root directory
- Check that previous steps completed successfully
- Verify output directories exist (`data/`, `outputs/`)

### Rate Limiting
- If you hit rate limits, the scripts will show errors
- Wait a few minutes and retry
- Consider reducing batch size in generation script if needed

---

## Verifying Results

After Step 5, check `outputs/evaluation_summary.json`:

```bash
cat outputs/evaluation_summary.json
```

Look for:
- `summary.accuracy_improvement` - How much better Genie is vs Baseline
- `summary.f1_improvement` - F1 score improvement
- `genie_vs_gold.accuracy` - Genie's accuracy against gold labels
- `baseline_vs_gold.accuracy` - Baseline's accuracy against gold labels

