# EduPilot RAG Evaluation Pipeline

Automated quality measurement for the EduPilot AI chatbot using two complementary frameworks.

---

## What is this?

| Framework | Purpose | When to run |
|-----------|---------|-------------|
| **Ragas** | Dataset-level, offline evaluation — scores faithfulness, answer relevancy, context precision, and context recall over a golden test set | Manually, before a release or after major changes to the RAG pipeline |
| **DeepEval** | Pytest-native regression tests — same metrics but integrated into CI so failures block merges | As part of the CI/CD pipeline via `deepeval test run` |

---

## Current scope

> **⚠ This evaluation currently covers the Scholarship Agent only.**
>
> The architecture is designed to extend to the Internship, Hackathon, and Jobs agents once their respective data pipelines are populated. Each agent will get its own golden dataset file and can be registered in `eval.py` under `/api/v1/eval/results/{agent}`.

---

## Architecture

```
golden_dataset_scholarship.json   (18 hand-curated Q&A pairs)
            ↓
    ragas_eval.py                 (calls the RAG pipeline, runs 4 metrics)
            ↓
    eval/results/ragas_results_<ts>.csv
            ↓
    services/app/api/routes/eval.py    → GET /api/v1/eval/results
            ↓
    app/app/dashboard/eval/page.tsx    (dashboard metric scorecards)
```

---

## Running Ragas evaluation

```bash
cd services

# Activate your venv first
source venv/bin/activate          # Linux/Mac
.\venv\Scripts\Activate.ps1       # Windows

# Run the full evaluation (takes ~5–15 min depending on judge model speed)
python eval/ragas_eval.py

# Print a presentation-ready markdown table from the latest results
python eval/summarize_results.py
```

Results are saved to `eval/results/ragas_results_<timestamp>.csv`.

---

## Running DeepEval tests

```bash
cd services

# Via DeepEval CLI (recommended — rich breakdown per test case):
deepeval test run tests/test_rag_quality_scholarship.py

# Via standard pytest (no LLM judge — structure/import check only):
python -m pytest tests/test_rag_quality_scholarship.py -v
```

---

## Swapping the judge model

The judge LLM is configured entirely via environment variables:

```bash
# Default — gemma4:cloud via local/cloud Ollama (no API key needed)
export JUDGE_PROVIDER=ollama
export JUDGE_MODEL=gemma4:cloud

# OpenRouter (free models available)
export JUDGE_PROVIDER=openrouter
export JUDGE_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
export OPENROUTER_API_KEY=your_key_here

# Anthropic Claude
export JUDGE_PROVIDER=anthropic
export JUDGE_MODEL=claude-sonnet-4-5
export ANTHROPIC_API_KEY=your_key_here
```

See `eval/judge_config.py` for the full implementation.

---

## Why a different judge model?

The generation model (`gpt-oss:120b-cloud`) must **not** judge its own outputs.

**Self-preference bias** is a well-documented failure mode: LLMs consistently rate
outputs from their own model family higher than independent evaluators do, because
they share the same distribution of phrasing, reasoning style, and knowledge.

Using `gemma4:cloud` (Google Gemma family) as the judge for a generation model
from a different family gives an independent, unbiased evaluation signal.

This is the same principle used in RLHF reward modelling — the judge and the actor
should not be the same model.

---

## Metrics

| Metric | What it measures | Passing threshold |
|--------|-----------------|-------------------|
| **Faithfulness** | Every claim in the answer is grounded in the retrieved context — measures hallucination | 0.70 |
| **Answer Relevancy** | The answer actually addresses what the question asked | 0.70 |
| **Context Precision** | The retrieved chunks are relevant to the question (retrieval signal-to-noise) | 0.70 |
| **Context Recall** | The retrieved chunks cover the information needed to answer correctly | 0.70 |

---

## Dashboard integration

The latest results are served read-only from:

```
GET /api/v1/eval/results          → latest results (scholarship agent)
GET /api/v1/eval/results/{agent}  → by agent (for future multi-agent support)
```

The frontend dashboard page at `/dashboard/eval` fetches these results and displays
metric scorecards. **The endpoint never triggers a live evaluation run** — it only
reads the last saved CSV file. This prevents unexpected LLM API costs or page-load
latency for end users.

---

## Adding a new agent's evaluation

1. Create `eval/golden_dataset_<agent>.json` with 15–20 Q&A pairs
2. Update `ragas_eval.py` to optionally run on the new dataset (`--agent` flag)
3. Tag the new agent's CSV files with `agent=<name>` in the metadata columns
4. Register the new agent in `app/api/routes/eval.py` → `supported` list
5. Update the frontend `page.tsx` to display the new agent's card when available
