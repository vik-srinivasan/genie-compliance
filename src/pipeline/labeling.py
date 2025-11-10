import re, random
from typing import Dict, List
from src.utils.io import read_csv, write_csv

SAFE_PAT = r"require\s*\(\s*[^)]*>=\s*[^)]*\)"

def model_a(code: str) -> str:
    return "safe" if re.search(SAFE_PAT, code) else "unsafe"

def model_b(code: str) -> str:
    return "safe" if re.search(SAFE_PAT, re.sub(r"\s+"," ", code)) else "unsafe"

def model_c(code: str) -> str:
    base = "safe" if re.search(SAFE_PAT, code) else "unsafe"
    return ("unsafe" if base=="safe" else "safe") if random.random() < 0.12 else base

def label_batch(rows: List[Dict]) -> List[Dict]:
    out = []
    for r in rows:
        code = r["code"]
        a = model_a(code)
        b = model_b(code)
        c = model_c(code)
        agree = (a == b == c)
        final_label = a if agree else r["label"]  # simulate human resolution
        out.append({
            "id": r["id"],
            "gold_label": r["label"],
            "model_a": a,
            "model_b": b,
            "model_c": c,
            "all_agree": str(agree).lower(),
            "final_label": final_label
        })
    return out

def run(input_csv: str, output_csv: str):
    rows = read_csv(input_csv)
    labeled = label_batch(rows)
    write_csv(output_csv, labeled,
              fieldnames=["id","gold_label","model_a","model_b","model_c","all_agree","final_label"])
