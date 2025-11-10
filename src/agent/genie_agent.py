import re
from typing import Dict

REQ = re.compile(r"require\s*\(\s*[^)]*>=\s*[^)]*\)")

def classify_and_explain(code: str) -> Dict:
    lines = code.splitlines()
    cite = None
    for i, line in enumerate(lines, start=1):
        if REQ.search(line):
            cite = i
            break
    status = "safe" if cite is not None else "unsafe"
    explanation = (
        f"Detected balance check via require(... >= ...) on line {cite}."
        if cite is not None else
        "No balance check (require(... >= ...)) found before updating balances."
    )
    return {"status": status, "citation_line": cite, "explanation": explanation}
