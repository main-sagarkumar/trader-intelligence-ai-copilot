"""Tests for semantic LLM-judge metrics."""

import asyncio
from collections.abc import Sequence

import pytest
from langchain_core.messages import BaseMessage

from trader_intelligence_ai_copilot.evaluation.answer_quality import AnswerCase
from trader_intelligence_ai_copilot.evaluation.semantic_judge import SemanticJudge
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider


class FakeJudgeLLM(BaseLLMProvider):
    async def generate_response(self, messages: Sequence[BaseMessage]) -> str:
        assert "retrieved_contexts" in str(messages[-1].content)
        return '{"groundedness": 0.8, "answer_relevance": 0.9, "faithfulness": 0.75}'


def build_case() -> AnswerCase:
    return AnswerCase(
        id="semantic",
        question="What is volatility?",
        answer="Volatility describes variability.",
        sources=("guide.pdf",),
        expected_facts={},
        expected_sources=("guide.pdf",),
        retrieved_contexts=("Volatility describes variability.",),
    )


def test_semantic_scores_and_derived_hallucination_rate() -> None:
    scores = asyncio.run(SemanticJudge(FakeJudgeLLM()).evaluate_case(build_case()))
    assert scores.groundedness == 0.8
    assert scores.hallucination_rate == pytest.approx(0.2)
    assert scores.answer_relevance == 0.9
    assert scores.faithfulness == 0.75


def test_rejects_out_of_range_judge_score() -> None:
    with pytest.raises(ValueError):
        SemanticJudge._parse_scores(
            '{"groundedness": 1.2, "answer_relevance": 1, "faithfulness": 1}'
        )
