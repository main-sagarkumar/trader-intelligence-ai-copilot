"""Input safety checks executed after authorization and before retrieval."""

from trader_intelligence_ai_copilot.guardrails.models import GuardrailResult
from trader_intelligence_ai_copilot.guardrails.pii import PIIRedactor


class InputGuardrail:
    _INJECTION_MARKERS = (
        "ignore previous instructions",
        "ignore all instructions",
        "reveal your system prompt",
        "show your system prompt",
        "bypass authorization",
        "disable guardrails",
    )
    _FINANCIAL_MARKERS = (
        "guarantee profit",
        "guaranteed profit",
        "exactly what to buy",
        "tell me what to buy",
        "risk-free trade",
    )
    _FINANCIAL_RESPONSE = (
        "I can provide educational analysis and explain risks, but I cannot "
        "guarantee profits or give definitive instructions to execute a trade."
    )

    @classmethod
    def evaluate(cls, text: str) -> GuardrailResult:
        normalized = text.lower()
        if any(marker in normalized for marker in cls._INJECTION_MARKERS):
            return GuardrailResult(
                allowed=False,
                text="",
                reasons=("prompt_injection",),
                risk_level="high",
            )

        redacted, pii_types = PIIRedactor.redact(text)
        reasons = tuple(f"pii_redacted:{item}" for item in pii_types)
        financial = any(marker in normalized for marker in cls._FINANCIAL_MARKERS)
        if financial:
            return GuardrailResult(
                allowed=True,
                text=redacted,
                reasons=(*reasons, "financial_advice_boundary"),
                risk_level="medium",
                intervention_response=cls._FINANCIAL_RESPONSE,
            )
        return GuardrailResult(True, redacted, reasons, "medium" if reasons else "low")
