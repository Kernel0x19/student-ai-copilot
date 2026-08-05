"""
Results summary script — reads the latest Ragas evaluation CSV and prints
a presentation-ready markdown table.

Usage:
    cd services
    python eval/summarize_results.py

Output format:
    | Metric             | Avg  | Min  | Max  |
    |--------------------|------|------|------|
    | faithfulness       | 0.91 | 0.80 | 1.00 |
    ...
"""
import csv
import glob
import sys
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
METRICS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]

METRIC_LABELS = {
    "faithfulness":      "Faithfulness",
    "answer_relevancy":  "Answer Relevancy",
    "context_precision": "Context Precision",
    "context_recall":    "Context Recall",
}


def find_latest_csv() -> Path | None:
    pattern = str(RESULTS_DIR / "ragas_results_*.csv")
    files = sorted(glob.glob(pattern), reverse=True)
    return Path(files[0]) if files else None


def load_scores(csv_path: Path) -> dict:
    """Load per-row metric scores from the CSV."""
    scores: dict[str, list[float]] = {m: [] for m in METRICS}
    metadata = {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        for row in rows:
            for metric in METRICS:
                if metric in row and row[metric]:
                    try:
                        scores[metric].append(float(row[metric]))
                    except ValueError:
                        pass
        if rows:
            metadata["agent"]        = rows[0].get("agent", "scholarship")
            metadata["evaluated_at"] = rows[0].get("evaluated_at", "unknown")
            metadata["sample_size"]  = rows[0].get("sample_size", len(rows))

    return scores, metadata


def print_markdown_table(scores: dict, metadata: dict, csv_path: Path) -> None:
    print()
    print("## EduPilot AI Quality Report — Scholarship Agent")
    print()
    print(f"> **Agent:** {metadata.get('agent', 'scholarship').title()}")
    print(f"> **Evaluated:** {metadata.get('evaluated_at', 'N/A')}  ")
    print(f"> **Sample size:** {metadata.get('sample_size', 'N/A')} questions  ")
    print(f"> **Source:** `{csv_path.name}`")
    print()

    # Table header
    col_w = 22
    print(f"| {'Metric':<{col_w}} | {'Avg':>6} | {'Min':>6} | {'Max':>6} |")
    print(f"|{'-'*(col_w+2)}|{'-'*8}|{'-'*8}|{'-'*8}|")

    for metric in METRICS:
        vals = scores.get(metric, [])
        label = METRIC_LABELS.get(metric, metric)
        if vals:
            avg = round(sum(vals) / len(vals), 2)
            mn  = round(min(vals), 2)
            mx  = round(max(vals), 2)
            print(f"| {label:<{col_w}} | {avg:>6.2f} | {mn:>6.2f} | {mx:>6.2f} |")
        else:
            print(f"| {label:<{col_w}} | {'N/A':>6} | {'N/A':>6} | {'N/A':>6} |")

    print()
    print("> Scores are 0–1 (higher is better). Threshold for passing CI: **0.70**.")
    print("> Judge model: `gemma4:cloud` — different family from generation model")
    print("> to avoid self-preference bias.")
    print()


def main() -> None:
    csv_path = find_latest_csv()
    if not csv_path:
        print(
            f"No results CSV found in {RESULTS_DIR}.\n"
            "Run `python eval/ragas_eval.py` first to generate results.",
            file=sys.stderr,
        )
        sys.exit(1)

    scores, metadata = load_scores(csv_path)
    print_markdown_table(scores, metadata, csv_path)


if __name__ == "__main__":
    main()
