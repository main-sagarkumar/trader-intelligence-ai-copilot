"""Deterministic answer-quality metrics for recorded model predictions."""

import json
import re
from dataclasses import dataclass, field, fields
from pathlib import Path

from trader_intelligence_ai_copilot.guardrails.pii import PIIRedactor


@dataclass(frozen=True, slots=True)
class AnswerCase:
    id: str
    question: str
    answer: str
    sources: tuple[str, ...]
    expected_facts: dict[str, str | int | float]
    expected_sources: tuple[str, ...]
    forbidden_claims: tuple[str, ...] = ()
    required_policy_terms: tuple[str, ...] = ()
    detected_pii: tuple[str, ...] = ()
    latency_ms: float = 0.0
    model_version: str = "unknown"
    prompt_version: str = "unknown"
    retrieved_contexts: tuple[str, ...] = ()
    trader_facts: dict[str, str | int | float | None] = field(default_factory=dict)
    reference_answer: str = ""


@dataclass(frozen=True, slots=True)
class AnswerQualityScores:
    fact_accuracy: float
    forbidden_claim_compliance: float
    citation_precision: float
    citation_recall: float
    pii_safety: float
    financial_policy_compliance: float


@dataclass(frozen=True, slots=True)
class AnswerQualityReport:
    case_count: int
    averages: AnswerQualityScores
    per_case: dict[str, AnswerQualityScores]
    passed: bool


class AnswerQualityEvaluator:
    @staticmethod
    def load_cases(path: Path) -> list[AnswerCase]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [
            AnswerCase(
                **{
                    **item,
                    "sources": tuple(item.get("sources", ())),
                    "expected_sources": tuple(item.get("expected_sources", ())),
                    "forbidden_claims": tuple(item.get("forbidden_claims", ())),
                    "required_policy_terms": tuple(
                        item.get("required_policy_terms", ())
                    ),
                    "detected_pii": tuple(item.get("detected_pii", ())),
                    "retrieved_contexts": tuple(item.get("retrieved_contexts", ())),
                    "trader_facts": dict(item.get("trader_facts", {})),
                }
            )
            for item in payload
        ]

    @classmethod
    def evaluate_case(cls, case: AnswerCase) -> AnswerQualityScores:
        answer = case.answer.lower()
        fact_matches = [
            cls._contains_value(answer, value)
            for value in case.expected_facts.values()
        ]
        fact_accuracy = (
            sum(fact_matches) / len(fact_matches) if fact_matches else 1.0
        )
        forbidden_compliance = float(
            not any(claim.lower() in answer for claim in case.forbidden_claims)
        )

        actual_sources = set(case.sources)
        expected_sources = set(case.expected_sources)
        citation_precision = (
            len(actual_sources & expected_sources) / len(actual_sources)
            if actual_sources
            else float(not expected_sources)
        )
        citation_recall = (
            len(actual_sources & expected_sources) / len(expected_sources)
            if expected_sources
            else 1.0
        )
        _, pii_types = PIIRedactor.redact(case.answer)
        pii_safety = float(not pii_types and not case.detected_pii)
        financial_compliance = float(
            all(term.lower() in answer for term in case.required_policy_terms)
        )
        return AnswerQualityScores(
            fact_accuracy,
            forbidden_compliance,
            citation_precision,
            citation_recall,
            pii_safety,
            financial_compliance,
        )

    @classmethod
    def run(
        cls, cases: list[AnswerCase], threshold: float = 1.0
    ) -> AnswerQualityReport:
        if not cases:
            raise ValueError("At least one answer case is required.")
        per_case = {case.id: cls.evaluate_case(case) for case in cases}
        count = len(cases)
        averages = AnswerQualityScores(
            **{
                field: sum(getattr(scores, field) for scores in per_case.values())
                / count
                for field in AnswerQualityScores.__dataclass_fields__
            }
        )
        return AnswerQualityReport(
            count,
            averages,
            per_case,
            all(getattr(averages, field.name) >= threshold for field in fields(averages)),
        )

    @staticmethod
    def _contains_value(answer: str, value: str | int | float) -> bool:
        rendered = str(value).lower()
        if isinstance(value, (int, float)):
            return (
                re.search(
                    rf"(?<![\d.]){re.escape(rendered)}(?![\d.]?\d)",
                    answer,
                )
                is not None
            )
        return rendered in answer
