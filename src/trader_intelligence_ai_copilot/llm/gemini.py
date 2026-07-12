from collections.abc import Sequence
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.utils.message_parser import extract_text


class GeminiProvider(BaseLLMProvider):
    """Gemini implementation."""

    def __init__(self) -> None:

        settings = get_settings()

        self.model = ChatGoogleGenerativeAI(
            model=settings.llm.model,
            google_api_key=settings.credentials.gemini_api_key.get_secret_value(),
            temperature=settings.llm.temperature,
        )

    async def generate_response(
        self,
        messages: Sequence[BaseMessage],
    ) -> str:

        response = await self.model.ainvoke(messages)

        return extract_text(response)