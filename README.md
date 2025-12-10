# Genie Compliance Inference System

A comprehensive system for analyzing Solidity smart contract safety using structured genie worksheets and LLM-based classification. This project implements a complete pipeline from contract generation to evaluation, comparing baseline LLM classification against genie worksheet-structured reasoning.

## Overview

This repository provides:
1. **Contract Generation** - Generate 250 Solidity contract snippets using GPT
2. **Multi-LLM Labeling** - Create gold labels using simulated multi-LLM consensus
3. **Baseline Classifier** - Single-shot LLM classification without worksheets
4. **Genie Classifier** - Worksheet-structured LLM classification with detailed reasoning
5. **Evaluation Module** - Compare all methods against gold labels
6. **Web Chatbot Interface** - Interactive frontend for contract analysis and fixing assistance

The system detects safety issues in ERC20-like `transfer()` functions, specifically checking for balance verification patterns like `require(balance >= amount)` and other security vulnerabilities.

## Prerequisites

1. **Python 3.8+**
2. **OpenAI API Key** - Required for all LLM operations
3. **Virtual Environment** (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd genie-compliance-infer
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**
   Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```
   Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Quick Start

### Full Pipeline Execution

Run the complete pipeline from contract generation to evaluation:

```bash
# Activate virtual environment
source .venv/bin/activate

# Step 1: Generate 250 contracts
python -m scripts.01_generate_contracts

# Step 2: Label contracts with multi-LLM pipeline
python -m scripts.02_label_contracts_multi_llm

# Step 3: Run baseline inference
python -m scripts.03_run_baseline_inference

# Step 4: Run genie worksheet inference
python -m scripts.04_run_genie_inference

# Step 5: Run evaluation
python -m scripts.05_run_evaluation
```

### Web Chatbot Interface

Start the interactive web interface for contract analysis:

```bash
python -m scripts.run_chatbot
```

Then open your browser to the port specified in the output.

## Project Structure

```
genie-compliance-infer/
├── data/
│   ├── contracts_raw.csv          # Generated contracts
│   └── contracts_labeled.csv      # Gold-labeled dataset
├── genie/
│   └── worksheet_template.csv     # Genie worksheet schema
├── outputs/
│   ├── baseline_inference.csv     # Baseline predictions
│   ├── genie_inference.csv        # Genie predictions
│   ├── baseline_metrics.json       # Baseline metrics
│   ├── genie_metrics.json         # Genie metrics
│   ├── labeling_metrics.json      # Labeling statistics
│   └── evaluation_summary.json    # Comparison results
├── src/
│   ├── generation/                # Contract generation
│   ├── pipeline/                  # Labeling pipeline
│   ├── agents/                    # Classifiers (baseline & genie)
│   ├── evaluation/                # Evaluation module
│   ├── utils/                     # Utility functions
│   └── web/                       # Web chatbot interface
├── scripts/                       # Execution scripts
└── tests/                         # Test files
```

## Output Files

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


## Model Configuration

All experiments use OpenAI's `gpt-4o-mini` model by default. You can override this by setting the `OPENAI_MODEL` environment variable:

```bash
export OPENAI_MODEL=gpt-4o  # or another OpenAI model
```

Default settings:
- **Temperature**: 0.0 for classification tasks, 0.7 for chat assistance
- **Max tokens**: 10 for labeling, 200 for baseline, 1000 for genie