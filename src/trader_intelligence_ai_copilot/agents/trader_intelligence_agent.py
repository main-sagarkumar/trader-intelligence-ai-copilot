"""Agent for trader-specific intelligence retrieval."""

from langchain_core.documents import Document

from trader_intelligence_ai_copilot.repositories.trader_repository import TraderRepository
from trader_intelligence_ai_copilot.retrieval.base import BaseRetriever
from trader_intelligence_ai_copilot.trader import TraderProfile


class TraderIntelligenceAgent:
    """Retrieve a trader profile and trader-intelligence knowledge documents."""

    def __init__(self, trader_repository: TraderRepository, retriever: BaseRetriever) -> None:
        self._trader_repository = trader_repository
        self._retriever = retriever

    def retrieve(self, question: str, trader_id: str) -> tuple[TraderProfile | None, list[Document]]:
        """Return structured trader data and restricted intelligence documents."""
        return (
            self._trader_repository.get_by_id(trader_id),
            self._retriever.retrieve(
                question,
                metadata_filter={"category": "trader_intelligence"},
                search_type="mmr",
            ),
        )
