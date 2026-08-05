"""
Ragas evaluation script for the EduPilot Scholarship Agent.

Usage:
    cd services
    python eval/ragas_eval.py

Metrics evaluated:
  - faithfulness        : Is the answer grounded in the retrieved contexts?
  - answer_relevancy    : Does the answer address the question?
  - context_precision   : Are retrieved chunks actually relevant to the question?
  - context_recall      : Do retrieved chunks cover the ground truth information?

Judge model: gemma4:cloud via Ollama (default) — different family from the
generation model (gpt-oss:120b-cloud) to avoid self-preference bias.
Override with JUDGE_PROVIDER env var (see eval/judge_config.py).

Results are saved to eval/results/ragas_results_<timestamp>.csv
"""
import asyncio
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure services/ is on the Python path when run directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)
from ragas.run_config import RunConfig

from app.agents.chatbot import query_scholarship_with_context
from eval.judge_config import get_judge_llm, get_judge_embeddings

GOLDEN_DATASET = Path(__file__).parent / "golden_dataset_scholarship.json"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


async def collect_rag_outputs(golden: list[dict]) -> list[dict]:
    """Call the RAG pipeline for each golden question and collect outputs."""
    rows = []
    total = len(golden)
    for i, item in enumerate(golden, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]
        print(f"  [{i}/{total}] Querying: {question[:70]}...")
        try:
            result = await query_scholarship_with_context(question)
            answer = result["answer"]
            contexts = result["contexts"] or ["No context retrieved."]
        except Exception as exc:
            print(f"    WARNING: query failed — {exc}")
            answer = "[retrieval error]"
            contexts = ["No context retrieved."]

        rows.append({
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "ground_truth": ground_truth,
        })
    return rows


def build_ragas_dataset(rows: list[dict]) -> Dataset:
    """Convert collected rows into a Ragas-compatible HuggingFace Dataset."""
    return Dataset.from_dict({
        "question":     [r["question"]     for r in rows],
        "answer":       [r["answer"]       for r in rows],
        "contexts":     [r["contexts"]     for r in rows],
        "ground_truth": [r["ground_truth"] for r in rows],
    })


def save_results(result, rows: list[dict], timestamp: str) -> Path:
    """Save Ragas results to a timestamped CSV file."""
    csv_path = RESULTS_DIR / f"ragas_results_{timestamp}.csv"

    # Convert Ragas result to a DataFrame-friendly dict
    result_df = result.to_pandas()

    # Attach extra metadata columns
    result_df["agent"] = "scholarship"
    result_df["evaluated_at"] = timestamp
    result_df["sample_size"] = len(rows)

    result_df.to_csv(csv_path, index=False)
    print(f"\nResults saved → {csv_path}")
    return csv_path


def print_summary(result) -> None:
    """Print a formatted summary table of metric scores."""
    metrics = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    df = result.to_pandas()

    print("\n" + "=" * 58)
    print("  EduPilot Scholarship Agent — Ragas Evaluation Summary")
    print("=" * 58)
    header = f"{'Metric':<25} {'Avg':>8} {'Min':>8} {'Max':>8}"
    print(header)
    print("-" * 58)
    for metric in metrics:
        if metric in df.columns:
            col = df[metric].dropna()
            avg = col.mean()
            mn  = col.min()
            mx  = col.max()
            print(f"  {metric:<23} {avg:>8.4f} {mn:>8.4f} {mx:>8.4f}")
        else:
            print(f"  {metric:<23} {'N/A':>8}")
    print("=" * 58)
    print(f"  Sample size: {len(df)} questions")
    print("=" * 58 + "\n")


async def main() -> None:
    print("\n=== EduPilot Scholarship Agent — Ragas Evaluation ===\n")

    # Load golden dataset
    with open(GOLDEN_DATASET, encoding="utf-8") as f:
        golden = json.load(f)
    print(f"Loaded {len(golden)} golden questions from {GOLDEN_DATASET.name}\n")

    # Collect RAG pipeline outputs
    print("Step 1/3 — Running RAG pipeline for each question...")
    rows = await collect_rag_outputs(golden)

    # Build Ragas dataset
    print("\nStep 2/3 — Running Ragas evaluation (this may take a few minutes)...")
    dataset = build_ragas_dataset(rows)

    judge_llm = get_judge_llm()
    judge_embeddings = get_judge_embeddings()
    metrics = [
        Faithfulness(llm=judge_llm),
        AnswerRelevancy(llm=judge_llm, embeddings=judge_embeddings),
        ContextPrecision(llm=judge_llm),
        ContextRecall(llm=judge_llm),
    ]

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        run_config=RunConfig(max_workers=1, timeout=120)
    )

    # Save and print
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    print("\nStep 3/3 — Saving results...")
    save_results(result, rows, timestamp)
    print_summary(result)


if __name__ == "__main__":
    asyncio.run(main())
