"""Deterministic PII detection and redaction."""

import re


class PIIRedactor:
    _PATTERNS = (
        ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
        ("phone", re.compile(r"(?<!\d)(?:\+?91[-\s]?)?[6-9]\d{9}(?!\d)")),
        ("aadhaar", re.compile(r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)")),
        ("pan", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.I)),
        ("payment_card", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")),
    )

    @classmethod
    def redact(cls, text: str) -> tuple[str, tuple[str, ...]]:
        detected: list[str] = []
        redacted = text
        for label, pattern in cls._PATTERNS:
            redacted, count = pattern.subn(f"[REDACTED_{label.upper()}]", redacted)
            if count:
                detected.append(label)
        return redacted, tuple(detected)
