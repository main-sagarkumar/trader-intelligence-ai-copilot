"""Tests for privacy-safe request telemetry and readiness."""

from fastapi.testclient import TestClient
from loguru import logger

from trader_intelligence_ai_copilot.api.main import app
from trader_intelligence_ai_copilot.observability import metrics


def test_request_id_is_generated_and_preserved() -> None:
    client = TestClient(app)
    generated = client.get("/health")
    preserved = client.get("/health", headers={"X-Request-ID": "demo-request-123"})

    assert generated.headers["X-Request-ID"]
    assert preserved.headers["X-Request-ID"] == "demo-request-123"


def test_http_metrics_increment() -> None:
    metrics.reset()
    TestClient(app).get("/health")
    snapshot = metrics.snapshot()

    assert snapshot["counters"]["http_requests_total"] == 1
    assert snapshot["durations"]["http_request_duration_ms"]["count"] == 1


def test_request_log_does_not_contain_query_string() -> None:
    messages: list[str] = []
    sink = logger.add(lambda message: messages.append(str(message)), format="{extra}")
    try:
        TestClient(app).get("/health?secret=private-value")
    finally:
        logger.remove(sink)

    output = "".join(messages)
    assert "private-value" not in output
    assert "secret=" not in output


def test_readiness_returns_degraded_status(monkeypatch) -> None:
    monkeypatch.setattr(
        "trader_intelligence_ai_copilot.api.routers.health.check_readiness",
        lambda: {
            "configuration": "ready",
            "postgresql": "not_ready",
            "chroma": "ready",
        },
    )

    response = TestClient(app).get("/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
