from src.utils.io import read_csv, write_csv
from src.agent.genie_agent import classify_and_explain
from src.pipeline.inference_metrics import run as run_infer_metrics  # NEW
import os

DATA = "data/dataset.csv"
OUT = "outputs/inference.csv"
INFER_METRICS = "outputs/inference_metrics.json"  # NEW

def main():
    rows = read_csv(DATA)
    out_rows = []
    for r in rows:
        res = classify_and_explain(r["code"])
        out_rows.append({
            "id": r["id"],
            "gold_label": r["label"],
            "agent_status": res["status"],
            "citation_line": res["citation_line"],
            "explanation": res["explanation"]
        })
    os.makedirs("outputs", exist_ok=True)
    write_csv(OUT, out_rows, fieldnames=["id", "gold_label", "agent_status", "citation_line", "explanation"])
    print("Genie inference complete.")
    print(f"- Wrote {OUT}")

    # NEW: compute and save inference metrics
    run_infer_metrics(OUT, INFER_METRICS)
    print(f"- Wrote {INFER_METRICS}")

    # Write two example text outputs for quick viewing
    examples_dir = "outputs/examples"
    os.makedirs(examples_dir, exist_ok=True)
    if out_rows:
        with open(f"{examples_dir}/example_0.txt", "w") as f:
            f.write(out_rows[0]["explanation"] + "\n\n" + rows[0]["code"])
        if len(out_rows) > 1:
            with open(f"{examples_dir}/example_1.txt", "w") as f:
                f.write(out_rows[1]["explanation"] + "\n\n" + rows[1]["code"])
    print(f"- Wrote {examples_dir}/example_0.txt (and example_1.txt if available)")

if __name__ == "__main__":
    main()
