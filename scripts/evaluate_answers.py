"""Score recorded model predictions with deterministic answer evaluators."""

from dataclasses import fields
from pathlib import Path

from trader_intelligence_ai_copilot.evaluation.answer_quality import (
    AnswerQualityEvaluator,
)


def main() -> None:
    cases = AnswerQualityEvaluator.load_cases(
        Path("data/evaluation/answer_cases.json")
    )
    report = AnswerQualityEvaluator.run(cases)
    print(f"Cases: {report.case_count}")
    for field in fields(report.averages):
        print(
            f"{field.name.replace('_', ' ').title()}: "
            f"{getattr(report.averages, field.name):.1%}"
        )
    print(f"Answer quality gate: {'PASS' if report.passed else 'FAIL'}")
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
