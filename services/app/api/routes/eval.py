"""
Read-only eval results endpoint.

Serves the most recent Ragas evaluation results as JSON.
NEVER triggers a live evaluation run — results are pre-computed offline
via `python eval/ragas_eval.py` and read from the saved CSV file.

This is intentional: live evaluation on request would trigger judge-LLM
API calls on every page load, incurring unexpected cost and latency.

Endpoints:
  GET /api/v1/eval/results                   → latest results (all agents)
  GET /api/v1/eval/results/{agent}           → latest results for a specific agent
"""
import csv
import glob
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/eval", tags=["eval"])

# Path to the eval results directory (relative to services/)
_RESULTS_DIR = Path(__file__).resolve().parents[3] / "eval" / "results"

_METRIC_KEYS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]


class EvalResultsResponse(BaseModel):
    last_updated: str
    agent: str
    metrics: dict[str, Optional[float]]
    sample_size: int
    source_file: str


def _find_latest_csv(agent: str = "scholarship") -> Optional[Path]:
    """Return the most recently created ragas_results CSV for the given agent."""
    pattern = str(_RESULTS_DIR / "ragas_results_*.csv")
    files = sorted(glob.glob(pattern), reverse=True)
    for f in files:
        path = Path(f)
        # All current results are scholarship; when more agents are added
        # their CSVs can be prefixed accordingly.
        return path
    return None


def _parse_csv(csv_path: Path) -> EvalResultsResponse:
    """Parse the Ragas results CSV into the response model."""
    scores: dict[str, list[float]] = {m: [] for m in _METRIC_KEYS}
    agent = "scholarship"
    evaluated_at = ""
    sample_size = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        sample_size = len(rows)
        for row in rows:
            for metric in _METRIC_KEYS:
                val = row.get(metric, "").strip()
                if val and val.lower() not in ("nan", ""):
                    try:
                        scores[metric].append(float(val))
                    except ValueError:
                        pass
            if not evaluated_at:
                evaluated_at = row.get("evaluated_at", "")
            if row.get("agent"):
                agent = row["agent"]
            if row.get("sample_size"):
                try:
                    sample_size = int(row["sample_size"])
                except ValueError:
                    pass

    # Compute averages
    avg_metrics: dict[str, Optional[float]] = {}
    for metric in _METRIC_KEYS:
        vals = scores[metric]
        avg_metrics[metric] = round(sum(vals) / len(vals), 4) if vals else None

    # Parse timestamp — try ISO format first, fall back to file mtime
    if evaluated_at:
        try:
            # Strip trailing Z and parse
            ts = evaluated_at.rstrip("Z")
            dt = datetime.strptime(ts, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
            last_updated = dt.isoformat().replace("+00:00", "Z")
        except ValueError:
            last_updated = evaluated_at
    else:
        mtime = csv_path.stat().st_mtime
        last_updated = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z")

    return EvalResultsResponse(
        last_updated=last_updated,
        agent=agent,
        metrics=avg_metrics,
        sample_size=sample_size,
        source_file=csv_path.name,
    )


@router.get("/results", response_model=EvalResultsResponse)
def get_eval_results():
    """
    Returns the latest pre-computed RAG evaluation results for the Scholarship agent.

    This endpoint is read-only and never triggers a live eval run.
    Results are computed offline via `python eval/ragas_eval.py`.
    """
    csv_path = _find_latest_csv()
    if not csv_path or not csv_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "No evaluation results found. "
                "Run `python eval/ragas_eval.py` from the services/ directory "
                "to generate results."
            ),
        )
    return _parse_csv(csv_path)


@router.get("/results/{agent}", response_model=EvalResultsResponse)
def get_eval_results_by_agent(agent: str):
    """
    Returns the latest pre-computed evaluation results for a specific agent.

    Currently only 'scholarship' has a golden dataset. Internship, Hackathon,
    and Jobs agents will be added here as their data pipelines are populated.
    """
    supported = ["scholarship"]
    if agent not in supported:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No evaluation results for agent '{agent}'. "
                f"Currently supported: {supported}. "
                "Additional agents will be added as their golden datasets are created."
            ),
        )
    csv_path = _find_latest_csv(agent)
    if not csv_path or not csv_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No evaluation results found for agent '{agent}'.",
        )
    return _parse_csv(csv_path)
