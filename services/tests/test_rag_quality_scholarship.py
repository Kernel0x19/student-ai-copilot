"""
DeepEval pytest test suite for EduPilot Scholarship Agent RAG quality.

Usage:
    # Via DeepEval CLI (recommended — shows rich metric breakdown):
    deepeval test run services/tests/test_rag_quality_scholarship.py

    # Via standard pytest (runs structure checks without LLM judge):
    cd services && python -m pytest tests/test_rag_quality_scholarship.py -v

Metrics (threshold 0.7 each):
  - FaithfulnessMetric        : answers grounded in retrieved context
  - AnswerRelevancyMetric     : answers address the question
  - ContextualPrecisionMetric : retrieved chunks are relevant to the question

Judge model: configured via JUDGE_PROVIDER env var (default: gemma4:cloud).
See services/eval/judge_config.py for provider options.
"""
import asyncio
import json
import sys
from pathlib import Path

import pytest

# Ensure services/ root is on the path when run directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from app.agents.chatbot import query_scholarship_with_context

# ---------------------------------------------------------------------------
# Load golden dataset (subset for CI speed — first 15 entries)
# ---------------------------------------------------------------------------
GOLDEN_PATH = Path(__file__).resolve().parents[1] / "eval" / "golden_dataset_scholarship.json"

with open(GOLDEN_PATH, encoding="utf-8") as f:
    _ALL_GOLDEN = json.load(f)

# Use the first 15 entries for the DeepEval suite (keeps CI fast)
GOLDEN_SUBSET = _ALL_GOLDEN[:15]


# ---------------------------------------------------------------------------
# Helper — run async retrieval synchronously for pytest parametrize
# ---------------------------------------------------------------------------

def _run_rag(question: str) -> dict:
    """Run the async RAG query in a blocking context for pytest."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, query_scholarship_with_context(question))
                return future.result(timeout=120)
        else:
            return loop.run_until_complete(query_scholarship_with_context(question))
    except Exception as exc:
        return {"answer": f"[eval error: {exc}]", "contexts": []}


# ---------------------------------------------------------------------------
# Metric factories — threshold 0.7 for each
# ---------------------------------------------------------------------------
THRESHOLD = 0.7


def _faithfulness():
    return FaithfulnessMetric(threshold=THRESHOLD, verbose_mode=False)


def _answer_relevancy():
    return AnswerRelevancyMetric(threshold=THRESHOLD, verbose_mode=False)


def _context_precision():
    return ContextualPrecisionMetric(threshold=THRESHOLD, verbose_mode=False)


# ---------------------------------------------------------------------------
# Parametrized test — one LLMTestCase per golden dataset entry
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "golden_item",
    GOLDEN_SUBSET,
    ids=[f"q{i+1}_{item['category']}" for i, item in enumerate(GOLDEN_SUBSET)],
)
def test_scholarship_rag_quality(golden_item: dict):
    """
    RAG quality regression test for the EduPilot Scholarship Agent.

    Builds an LLMTestCase for each golden dataset entry and asserts that
    the RAG pipeline meets the 0.7 threshold for faithfulness, answer
    relevancy, and contextual precision.
    """
    question = golden_item["question"]
    expected_output = golden_item["ground_truth"]

    # Call the RAG pipeline
    result = _run_rag(question)
    actual_output = result["answer"]
    retrieval_context = result["contexts"] or ["No context retrieved."]

    # Build DeepEval test case
    test_case = LLMTestCase(
        input=question,
        actual_output=actual_output,
        expected_output=expected_output,
        retrieval_context=retrieval_context,
    )

    # Assert against all three metrics
    assert_test(
        test_case,
        metrics=[
            _faithfulness(),
            _answer_relevancy(),
            _context_precision(),
        ],
    )
