from functools import lru_cache

from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.config.enums.providers import EmbeddingProvider

from trader_intelligence_ai_copilot.embeddings.base import BaseEmbeddingProvider
from trader_intelligence_ai_copilot.embeddings.gemini import GeminiEmbeddingProvider


@lru_cache
def get_embedding_provider() -> BaseEmbeddingProvider:
    """Return the configured embedding provider."""

    settings = get_settings()

    match settings.embeddings.provider:
        case EmbeddingProvider.GEMINI:
            return GeminiEmbeddingProvider()

        case _:
            raise ValueError(
                f"Unsupported embedding provider: {settings.embeddings.provider}"
            )