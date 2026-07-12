"""Tests for sanitized LangSmith dataset and evaluator construction."""

from trader_intelligence_ai_copilot.evaluation.answer_quality import AnswerCase
from trader_intelligence_ai_copilot.evaluation.langsmith_adapter import (
    LangSmithEvaluationAdapter,
)


def test_examples_exclude_trader_profiles_and_raw_context() -> None:
    case = AnswerCase(
        id="safe",
        question="What is volatility?",
        answer="Expected variability.",
        sources=("guide.pdf",),
        expected_facts={"definition": "expected variability"},
        expected_sources=("guide.pdf",),
    )
    example = LangSmithEvaluationAdapter.examples([case])[0]

    assert set(example["inputs"]) == {"case_id", "question"}
    assert "answer" not in example["outputs"]
    assert "context" not in str(example).lower()


def test_code_evaluator_scores_valid_prediction() -> None:
    result = LangSmithEvaluationAdapter.deterministic_evaluator(
        {"case_id": "safe", "question": "What is volatility?"},
        {"answer": "Expected variability.", "sources": ["guide.pdf"]},
        {
            "expected_facts": {"definition": "expected variability"},
            "expected_sources": ["guide.pdf"],
            "forbidden_claims": [],
            "required_policy_terms": [],
        },
    )
    assert result == {"key": "deterministic_quality", "score": 1.0}
