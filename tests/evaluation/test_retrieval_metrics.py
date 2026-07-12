"""Tests for ranked information-retrieval metrics."""

import pytest

from trader_intelligence_ai_copilot.evaluation.retrieval_metrics import score_retrieval
from trader_intelligence_ai_copilot.evaluation.retrieval_runner import (
    RetrievalCase,
    RetrievalEvaluationRunner,
)


def test_scores_ranked_retrieval_at_k() -> None:
    scores = score_retrieval(
        ranked_ids=["relevant-a.pdf", "noise.pdf", "relevant-b.pdf"],
        relevance={"relevant-a.pdf": 3, "relevant-b.pdf": 2},
        k=3,
    )

    assert scores.precision_at_k == pytest.approx(2 / 3)
    assert scores.recall_at_k == 1.0
    assert scores.hit_rate_at_k == 1.0
    assert scores.reciprocal_rank == 1.0
    assert 0.95 < scores.ndcg_at_k < 0.96


def test_first_relevant_at_rank_two_changes_mrr() -> None:
    scores = score_retrieval(
        ["noise.pdf", "relevant.pdf"], {"relevant.pdf": 1}, k=2
    )
    assert scores.reciprocal_rank == 0.5
    assert scores.hit_rate_at_k == 1.0


def test_no_hit_scores_zero() -> None:
    scores = score_retrieval(["noise.pdf"], {"relevant.pdf": 3}, k=1)
    assert scores.precision_at_k == 0.0
    assert scores.recall_at_k == 0.0
    assert scores.hit_rate_at_k == 0.0
    assert scores.reciprocal_rank == 0.0
    assert scores.ndcg_at_k == 0.0


def test_runner_deduplicates_chunk_level_document_ids() -> None:
    case = RetrievalCase(
        id="deduplicate",
        question="question",
        relevance={"guide.pdf": 3},
    )
    report = RetrievalEvaluationRunner.run(
        [case], lambda _case, _k: ["guide.pdf", "guide.pdf", "noise.pdf"], k=2
    )

    assert report.averages.recall_at_k == 1.0
    assert report.averages.precision_at_k == 0.5


def test_project_retrieval_dataset_has_labels() -> None:
    from pathlib import Path

    cases = RetrievalEvaluationRunner.load_cases(
        Path("data/evaluation/retrieval_cases.json")
    )
    assert len(cases) >= 7
    assert all(case.relevance for case in cases)
