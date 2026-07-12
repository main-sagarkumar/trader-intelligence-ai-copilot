"""Models for deterministic golden-dataset evaluation."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class GoldenCase:
    id: str
    question: str = ""
    expected_route: str | None = None
    expected_categories: tuple[str, ...] = ()
    expected_guardrail: Literal["allow", "block", "intervene", "redact"] | None = None
    assigned_traders: tuple[str, ...] = ()
    requested_trader: str | None = None
    is_admin: bool = False
    expected_authorized: bool | None = None
    history: str = ""
    trader_id: str = "TRADER_101"
    expected_rewrite_contains: tuple[str, ...] = ()
    output_text: str | None = None
    has_sources: bool = True
    expected_output_reason: str | None = None


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    total_cases: int
    metrics: dict[str, float]
    failures: tuple[str, ...]
    passed: bool
