"""HTTP correlation and latency middleware."""

from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from trader_intelligence_ai_copilot.observability.context import reset_request_id, set_request_id
from trader_intelligence_ai_copilot.observability.events import log_event
from trader_intelligence_ai_copilot.observability.metrics import metrics


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        token = set_request_id(request_id)
        started = perf_counter()
        metrics.increment("http_requests_total")
        try:
            response = await call_next(request)
            if response.status_code >= 500:
                metrics.increment("http_errors_total")
            return response
        except Exception:
            metrics.increment("http_errors_total")
            raise
        finally:
            duration = (perf_counter() - started) * 1000
            metrics.observe("http_request_duration_ms", duration)
            log_event(
                "http_request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code if "response" in locals() else 500,
                success=(response.status_code < 500) if "response" in locals() else False,
                duration_ms=round(duration, 2),
            )
            if "response" in locals():
                response.headers["X-Request-ID"] = request_id
            reset_request_id(token)
