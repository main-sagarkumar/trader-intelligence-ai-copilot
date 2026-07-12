"""Structured guardrail decisions."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class GuardrailResult:
    allowed: bool
    text: str
    reasons: tuple[str, ...] = ()
    risk_level: Literal["low", "medium", "high"] = "low"
    intervention_response: str | None = None
