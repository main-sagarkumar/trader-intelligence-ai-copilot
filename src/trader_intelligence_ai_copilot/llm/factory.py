from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.config.enums.providers import LLMProvider

from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.llm.gemini import GeminiProvider


def get_llm() -> BaseLLMProvider:
    """Return the configured LLM provider."""

    settings = get_settings()

    match settings.llm.provider:
        case LLMProvider.GEMINI:
            return GeminiProvider()

        case _:
            raise ValueError(
                f"Unsupported LLM provider: {settings.llm.provider}"
            )