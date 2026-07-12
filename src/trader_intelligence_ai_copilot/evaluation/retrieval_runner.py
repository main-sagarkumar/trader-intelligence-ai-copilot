"""Run and aggregate labeled retrieval evaluation cases."""

import json
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable

from trader_intelligence_ai_copilot.evaluation.retrieval_metrics import (
    RetrievalScores,
    score_retrieval,
)


@dataclass(frozen=True, slots=True)
class RetrievalCase:
    id: str
    question: str
    relevance: dict[str, int]
    category: str | None = None


@dataclass(frozen=True, slots=True)
class RetrievalEvaluationReport:
    case_count: int
    averages: RetrievalScores
    per_case: dict[str, RetrievalScores]


class RetrievalEvaluationRunner:
    @staticmethod
    def load_cases(path: Path) -> list[RetrievalCase]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [RetrievalCase(**item) for item in payload]

    @staticmethod
    def run(
        cases: list[RetrievalCase],
        retrieve: Callable[[RetrievalCase, int], list[str]],
        k: int = 5,
    ) -> RetrievalEvaluationReport:
        if not cases:
            raise ValueError("At least one retrieval case is required.")
        per_case = {
            case.id: score_retrieval(
                _unique(retrieve(case, k)), case.relevance, k
            )
            for case in cases
        }
        count = len(per_case)
        averages = RetrievalScores(
            **{
                field: sum(getattr(scores, field) for scores in per_case.values())
                / count
                for field in RetrievalScores.__dataclass_fields__
            }
        )
        return RetrievalEvaluationReport(count, averages, per_case)


def _unique(document_ids: list[str]) -> list[str]:
    return list(dict.fromkeys(document_ids))
