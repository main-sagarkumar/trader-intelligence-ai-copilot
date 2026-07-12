"""Structured telemetry events that intentionally exclude user content."""

from loguru import logger

from trader_intelligence_ai_copilot.observability.context import request_id_context


def log_event(event: str, **safe_fields: object) -> None:
    """Write a structured event; callers must pass metadata, never content."""
    logger.bind(
        event=event,
        request_id=request_id_context.get(),
        **safe_fields,
    ).info(event)
