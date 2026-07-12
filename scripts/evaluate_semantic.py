"""Run opt-in semantic LLM evaluation over sanitized prediction artifacts."""

import argparse
import asyncio
from dataclasses import fields
from pathlib import Path

from trader_intelligence_ai_copilot.evaluation.answer_quality import AnswerQualityEvaluator
from trader_intelligence_ai_copilot.evaluation.semantic_judge import SemanticJudge
from trader_intelligence_ai_copilot.llm.factory import get_llm


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/evaluation/gemini-predictions.json"),
    )
    args = parser.parse_args()
    cases = AnswerQualityEvaluator.load_cases(args.input)
    report = await SemanticJudge(get_llm()).run(cases)
    print(f"Cases: {report.case_count}")
    for field in fields(report.averages):
        print(
            f"{field.name.replace('_', ' ').title()}: "
            f"{getattr(report.averages, field.name):.3f}"
        )


if __name__ == "__main__":
    asyncio.run(main())
