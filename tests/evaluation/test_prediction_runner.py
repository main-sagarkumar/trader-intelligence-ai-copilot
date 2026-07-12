"""Tests for privacy-safe model prediction artifacts."""

import asyncio
import json

from trader_intelligence_ai_copilot.evaluation.answer_quality import (
    AnswerCase,
    AnswerQualityEvaluator,
)
from trader_intelligence_ai_copilot.evaluation.prediction_runner import PredictionRunner


def build_case() -> AnswerCase:
    return AnswerCase(
        id="prediction",
        question="What is volatility?",
        answer="",
        sources=(),
        expected_facts={"definition": "expected variability"},
        expected_sources=("guide.pdf",),
    )


def test_runner_sanitizes_answer_and_records_pii_signal() -> None:
    async def target(_case):
        return "Expected variability. Contact trader@example.com", ["guide.pdf"]

    predictions = asyncio.run(
        PredictionRunner.run([build_case()], target, "gemini-test", "prompt-v1")
    )
    prediction = predictions[0]

    assert "trader@example.com" not in prediction.answer
    assert prediction.detected_pii == ("email",)
    assert prediction.model_version == "gemini-test"
    assert AnswerQualityEvaluator.evaluate_case(prediction).pii_safety == 0.0


def test_prediction_artifact_contains_no_raw_pii(tmp_path) -> None:
    async def target(_case):
        return "Email trader@example.com", []

    predictions = asyncio.run(
        PredictionRunner.run([build_case()], target, "model", "prompt")
    )
    output = tmp_path / "predictions.json"
    PredictionRunner.write(predictions, output)
    payload = output.read_text(encoding="utf-8")

    assert "trader@example.com" not in payload
    assert json.loads(payload)[0]["detected_pii"] == ["email"]
