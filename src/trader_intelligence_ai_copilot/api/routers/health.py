from fastapi import APIRouter, Response, status
from sqlalchemy import text

from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.schemas.health import HealthResponse, ReadinessResponse
from trader_intelligence_ai_copilot.database.session import get_engine
from trader_intelligence_ai_copilot.vectorstore.factory import get_vector_store

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
)
async def health_check() -> HealthResponse:
    settings = get_settings()

    return HealthResponse(
        status="healthy",
        app=settings.app.name,
        version=settings.app.version,
    )


def check_readiness() -> dict[str, str]:
    """Check local dependencies without calling an external LLM API."""
    settings = get_settings()
    components: dict[str, str] = {}
    required = (
        settings.database.url.get_secret_value(),
        settings.security.jwt_secret_key.get_secret_value(),
        settings.credentials.gemini_api_key.get_secret_value(),
    )
    components["configuration"] = "ready" if all(required) else "not_ready"

    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        components["postgresql"] = "ready"
    except Exception:
        components["postgresql"] = "not_ready"

    try:
        get_vector_store()
        components["chroma"] = "ready"
    except Exception:
        components["chroma"] = "not_ready"
    return components


@router.get("/ready", response_model=ReadinessResponse, summary="Readiness Check")
def readiness_check(response: Response) -> ReadinessResponse:
    components = check_readiness()
    ready = all(value == "ready" for value in components.values())
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(
        status="ready" if ready else "degraded",
        components=components,
    )
