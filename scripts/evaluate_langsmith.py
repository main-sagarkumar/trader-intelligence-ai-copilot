"""Upload sanitized predictions to an opt-in LangSmith experiment."""

import argparse
import os
from pathlib import Path

from langsmith import Client

from trader_intelligence_ai_copilot.evaluation.answer_quality import AnswerQualityEvaluator
from trader_intelligence_ai_copilot.evaluation.langsmith_adapter import (
    LangSmithEvaluationAdapter,
)


def main() -> None:
    if os.getenv("LANGSMITH_ENABLED", "false").lower() != "true":
        raise RuntimeError("Set LANGSMITH_ENABLED=true to permit sanitized upload.")
    if not os.getenv("LANGSMITH_API_KEY"):
        raise RuntimeError("LANGSMITH_API_KEY must be configured.")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/evaluation/gemini-predictions.json"),
    )
    args = parser.parse_args()
    cases = AnswerQualityEvaluator.load_cases(args.input)
    LangSmithEvaluationAdapter.run(Client(), cases)
    print(f"Uploaded {len(cases)} sanitized predictions to LangSmith.")


if __name__ == "__main__":
    main()
