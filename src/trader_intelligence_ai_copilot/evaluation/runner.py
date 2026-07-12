"""Offline deterministic evaluation runner."""

import json
from pathlib import Path

from trader_intelligence_ai_copilot.evaluation.models import (
    EvaluationReport,
    GoldenCase,
)
from trader_intelligence_ai_copilot.guardrails import InputGuardrail, OutputGuardrail
from trader_intelligence_ai_copilot.orchestration import IntentRouter
from trader_intelligence_ai_copilot.retrieval.query_rewriter import ConversationQueryRewriter


class EvaluationRunner:
    METRIC_NAMES = (
        "routing",
        "categories",
        "guardrails",
        "authorization",
        "memory_rewrite",
        "grounding",
    )

    @classmethod
    def load_cases(cls, path: Path) -> list[GoldenCase]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [
            GoldenCase(
                **{
                    **item,
                    "expected_categories": tuple(item.get("expected_categories", ())),
                    "assigned_traders": tuple(item.get("assigned_traders", ())),
                    "expected_rewrite_contains": tuple(item.get("expected_rewrite_contains", ())),
                }
            )
            for item in payload
        ]

    @classmethod
    def run(
        cls, cases: list[GoldenCase], threshold: float = 1.0
    ) -> EvaluationReport:
        correct = {name: 0 for name in cls.METRIC_NAMES}
        totals = {name: 0 for name in cls.METRIC_NAMES}
        failures: list[str] = []

        for case in cases:
            route = IntentRouter.classify(case.question) if case.question else None
            if case.expected_route is not None:
                cls._record("routing", route == case.expected_route, case.id, correct, totals, failures)
            if case.expected_categories:
                actual = IntentRouter.categories(route) if route is not None else ()
                cls._record(
                    "categories", set(actual) == set(case.expected_categories), case.id, correct, totals, failures
                )
            if case.expected_guardrail is not None:
                result = InputGuardrail.evaluate(case.question)
                actual_guardrail = cls._guardrail_outcome(result)
                cls._record(
                    "guardrails", actual_guardrail == case.expected_guardrail, case.id, correct, totals, failures
                )
            if case.expected_authorized is not None:
                authorized = case.is_admin or case.requested_trader in case.assigned_traders
                cls._record(
                    "authorization", authorized == case.expected_authorized, case.id, correct, totals, failures
                )
            if case.expected_rewrite_contains:
                rewritten = ConversationQueryRewriter.rewrite(
                    case.question, case.history, case.trader_id
                )
                matches = all(value in rewritten for value in case.expected_rewrite_contains)
                cls._record(
                    "memory_rewrite", matches, case.id, correct, totals, failures
                )
            if case.expected_output_reason is not None and case.output_text is not None:
                output = OutputGuardrail.evaluate(
                    case.output_text, case.trader_id, case.has_sources
                )
                cls._record(
                    "grounding",
                    case.expected_output_reason in output.reasons,
                    case.id,
                    correct,
                    totals,
                    failures,
                )

        metrics = {
            name: (correct[name] / totals[name] if totals[name] else 1.0)
            for name in cls.METRIC_NAMES
        }
        passed = not failures and all(score >= threshold for score in metrics.values())
        return EvaluationReport(len(cases), metrics, tuple(failures), passed)

    @staticmethod
    def _guardrail_outcome(result) -> str:
        if not result.allowed:
            return "block"
        if result.intervention_response:
            return "intervene"
        if any(reason.startswith("pii_redacted:") for reason in result.reasons):
            return "redact"
        return "allow"

    @staticmethod
    def _record(metric, passed, case_id, correct, totals, failures) -> None:
        totals[metric] += 1
        correct[metric] += int(passed)
        if not passed:
            failures.append(f"{case_id}: {metric}")
