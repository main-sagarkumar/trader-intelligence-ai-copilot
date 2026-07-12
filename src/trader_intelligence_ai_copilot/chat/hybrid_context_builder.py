"""Assembly of trader-specific and retrieved knowledge context."""

import logging

from trader_intelligence_ai_copilot.chat.context_builder import ContextBuilder
from trader_intelligence_ai_copilot.chat.hybrid_context_models import HybridContext
from trader_intelligence_ai_copilot.repositories.trader_repository import TraderRepository
from trader_intelligence_ai_copilot.retrieval.base import BaseRetriever

logger = logging.getLogger(__name__)


class HybridContextBuilder:
    """Build context from structured trader data and knowledge documents."""

    def __init__(
        self,
        trader_repository: TraderRepository,
        retriever: BaseRetriever,
    ) -> None:
        """Initialize the builder with structured and semantic data providers."""
        self._trader_repository = trader_repository
        self._retriever = retriever

    def build(
        self,
        question: str,
        trader_id: str,
        k: int = 5,
    ) -> HybridContext:
        """Assemble structured trader data and retrieved knowledge context."""
        trader_profile = self._trader_repository.get_by_id(trader_id)
        documents = self._retriever.retrieve(question, k=k)
        context_result = ContextBuilder.build_context(documents)

        logger.info(
            "Hybrid context assembled.",
            extra={
                "trader_profile_found": trader_profile is not None,
                "retrieved_document_count": len(documents),
            },
        )

        return HybridContext(
            user_question=question,
            trader_profile=trader_profile,
            retrieved_documents=documents,
            knowledge_context=context_result.context,
            sources=context_result.sources,
        )
