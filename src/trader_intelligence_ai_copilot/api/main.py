from fastapi import FastAPI

from trader_intelligence_ai_copilot.api.routers.health import router as health_router

from trader_intelligence_ai_copilot.api.routers.chat import router as chat_router
from trader_intelligence_ai_copilot.api.routers.auth import router as auth_router
from trader_intelligence_ai_copilot.api.routers.personalized_chat import (
    router as personalized_chat_router,
)
from trader_intelligence_ai_copilot.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(personalized_chat_router)
