from functools import lru_cache

from trader_intelligence_ai_copilot.retrieval.base import BaseRetriever
from trader_intelligence_ai_copilot.retrieval.vector_retriever import (
    VectorRetriever,
)
from trader_intelligence_ai_copilot.vectorstore.factory import (
    get_vector_store,
)


@lru_cache
def get_retriever() -> BaseRetriever:
    """Return the configured retriever."""

    return VectorRetriever(
        vector_store=get_vector_store(),
    )