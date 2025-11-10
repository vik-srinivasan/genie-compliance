# Genie Compliance Inference POC

This repository provides two entrypoints:
1) **Label generation** using simulated 3× LLMs with agreement/flag logic.
2) **Initial Genie agent inference** over labeled data; the agent explains a simple safety check with code citations.

The agent detects whether a `require(balance >= amount)`-style check exists in an ERC20-like `transfer()` function and explains the decision.

## Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Generate labels (3 "LLMs" + reconciliation)
python -m scripts.run_label_generation

# 2) Run initial Genie agent inference on the dataset
python -m scripts.run_genie_inference
```

### Outputs
- `outputs/labels.csv` — model_a/model_b/model_c predictions, agreement flag, final label.
- `outputs/metrics.json` — label-generation quality stats.
- `outputs/inference.csv` — Genie agent decisions and explanations by example.
- `outputs/examples/` — a few pretty-printed analyses for quick review.
