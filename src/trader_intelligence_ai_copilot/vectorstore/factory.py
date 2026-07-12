from functools import lru_cache

from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.vectorstore.base import BaseVectorStore
from trader_intelligence_ai_copilot.vectorstore.chroma import (
    ChromaVectorStore,
)


@lru_cache
def get_vector_store() -> BaseVectorStore:
    """Return the configured vector store."""

    settings = get_settings()

    match settings.vectorstore.provider:

        case "chroma":
            return ChromaVectorStore()

        case _:
            raise ValueError(
                f"Unsupported vector store: {settings.vectorstore.provider}"
            )