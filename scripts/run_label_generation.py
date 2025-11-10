from src.pipeline import labeling, metrics
import os

DATA = "data/dataset.csv"
LABELS = "outputs/labels.csv"
METRICS = "outputs/metrics.json"

def main():
    os.makedirs("outputs", exist_ok=True)
    labeling.run(DATA, LABELS)
    metrics.run(LABELS, METRICS)
    print("Label generation complete.")
    print(f"- Wrote {LABELS}")
    print(f"- Wrote {METRICS}")

if __name__ == "__main__":
    main()
