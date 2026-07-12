from fastapi import APIRouter

from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.schemas.health import HealthResponse

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