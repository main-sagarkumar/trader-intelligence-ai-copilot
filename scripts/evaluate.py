"""Run the deterministic AI regression suite."""

from pathlib import Path

from trader_intelligence_ai_copilot.evaluation import EvaluationRunner


def main() -> None:
    path = Path("data/evaluation/golden_cases.json")
    report = EvaluationRunner.run(EvaluationRunner.load_cases(path))
    print(f"Cases: {report.total_cases}")
    for name, score in report.metrics.items():
        print(f"{name.replace('_', ' ').title()}: {score:.1%}")
    if report.failures:
        print("Failures:")
        for failure in report.failures:
            print(f"- {failure}")
    if not report.passed:
        raise SystemExit(1)
    print("Evaluation gate: PASS")


if __name__ == "__main__":
    main()
