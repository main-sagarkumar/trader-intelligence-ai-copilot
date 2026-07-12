"""Tests for deterministic answer-quality scoring."""

from pathlib import Path

from trader_intelligence_ai_copilot.evaluation.answer_quality import (
    AnswerCase,
    AnswerQualityEvaluator,
)


def test_project_recorded_answers_pass_quality_gate() -> None:
    cases = AnswerQualityEvaluator.load_cases(
        Path("data/evaluation/answer_cases.json")
    )
    report = AnswerQualityEvaluator.run(cases)

    assert report.case_count >= 4
    assert report.passed


def test_detects_wrong_fact_invalid_citation_and_pii() -> None:
    case = AnswerCase(
        id="bad_answer",
        question="Why am I Cluster 3?",
        answer="You are Cluster 4. Email trader@example.com for details.",
        sources=("unrelated.pdf",),
        expected_facts={"cluster": 3},
        expected_sources=("cluster_explanations.pdf",),
        forbidden_claims=("cluster 4",),
    )
    scores = AnswerQualityEvaluator.evaluate_case(case)

    assert scores.fact_accuracy == 0.0
    assert scores.forbidden_claim_compliance == 0.0
    assert scores.citation_precision == 0.0
    assert scores.citation_recall == 0.0
    assert scores.pii_safety == 0.0


def test_numeric_fact_matching_uses_boundaries() -> None:
    case = AnswerCase(
        id="numeric_boundary",
        question="cluster",
        answer="The cluster is 30.",
        sources=(),
        expected_facts={"cluster": 3},
        expected_sources=(),
    )
    assert AnswerQualityEvaluator.evaluate_case(case).fact_accuracy == 0.0
