from trader_intelligence_ai_copilot.application.chat_service import ChatService
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.llm.factory import get_llm


def get_llm_provider() -> BaseLLMProvider:
    return get_llm()


def get_chat_service() -> ChatService:
    return ChatService(
        llm=get_llm_provider(),
    )