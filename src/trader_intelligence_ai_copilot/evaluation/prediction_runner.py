"""Generate privacy-sanitized predictions for deterministic evaluation."""

import json
from collections.abc import Awaitable, Callable
from dataclasses import asdict, replace
from pathlib import Path
from time import perf_counter

from trader_intelligence_ai_copilot.evaluation.answer_quality import AnswerCase
from trader_intelligence_ai_copilot.guardrails.pii import PIIRedactor


PredictionTarget = Callable[
    [AnswerCase], Awaitable[tuple[str, list[str]]]
]


class PredictionRunner:
    @staticmethod
    async def run(
        cases: list[AnswerCase],
        target: PredictionTarget,
        model_version: str,
        prompt_version: str,
    ) -> list[AnswerCase]:
        predictions: list[AnswerCase] = []
        for case in cases:
            started = perf_counter()
            answer, sources = await target(case)
            latency_ms = (perf_counter() - started) * 1000
            sanitized_answer, pii_types = PIIRedactor.redact(answer)
            predictions.append(
                replace(
                    case,
                    answer=sanitized_answer,
                    sources=tuple(dict.fromkeys(sources)),
                    detected_pii=pii_types,
                    latency_ms=latency_ms,
                    model_version=model_version,
                    prompt_version=prompt_version,
                )
            )
        return predictions

    @staticmethod
    def write(cases: list[AnswerCase], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps([asdict(case) for case in cases], indent=2),
            encoding="utf-8",
        )
