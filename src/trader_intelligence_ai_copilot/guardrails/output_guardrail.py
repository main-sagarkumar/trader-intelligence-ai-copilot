"""Output checks for secrets, PII, grounding, and cross-trader leakage."""

import re

from trader_intelligence_ai_copilot.guardrails.models import GuardrailResult
from trader_intelligence_ai_copilot.guardrails.pii import PIIRedactor


class OutputGuardrail:
    _SECRET_PATTERNS = (
        re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
        re.compile(r"\b(?:postgresql|mysql)://\S+", re.I),
        re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
        re.compile(r"password_hash\s*[:=]\s*\S+", re.I),
    )
    _SAFE_OUTPUT = "I cannot provide that response because it may expose sensitive information."
    _UNGROUNDED_OUTPUT = (
        "I do not have sufficient retrieved context to answer that reliably."
    )

    @classmethod
    def evaluate(
        cls, text: str, trader_id: str, has_sources: bool
    ) -> GuardrailResult:
        if any(pattern.search(text) for pattern in cls._SECRET_PATTERNS):
            return GuardrailResult(
                False, cls._SAFE_OUTPUT, ("secret_exposure",), "high"
            )

        mentioned_traders = set(re.findall(r"\bTRADER_\d+\b", text, re.I))
        if any(item.upper() != trader_id.upper() for item in mentioned_traders):
            return GuardrailResult(
                False, cls._SAFE_OUTPUT, ("cross_trader_leakage",), "high"
            )

        redacted, pii_types = PIIRedactor.redact(text)
        reasons = tuple(f"pii_redacted:{item}" for item in pii_types)
        if not has_sources:
            return GuardrailResult(
                True,
                cls._UNGROUNDED_OUTPUT,
                (*reasons, "insufficient_grounding"),
                "medium",
            )
        return GuardrailResult(True, redacted, reasons, "medium" if reasons else "low")
