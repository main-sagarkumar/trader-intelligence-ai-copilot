"""Tests for the deterministic golden-dataset regression gate."""

from pathlib import Path

from trader_intelligence_ai_copilot.evaluation import EvaluationRunner, GoldenCase


def test_project_golden_dataset_passes() -> None:
    cases = EvaluationRunner.load_cases(Path("data/evaluation/golden_cases.json"))
    report = EvaluationRunner.run(cases)

    assert report.total_cases >= 15
    assert report.passed
    assert all(score == 1.0 for score in report.metrics.values())


def test_regression_produces_failure() -> None:
    report = EvaluationRunner.run(
        [GoldenCase(id="wrong_route", question="What is volatility?", expected_route="trader")]
    )

    assert not report.passed
    assert report.failures == ("wrong_route: routing",)
