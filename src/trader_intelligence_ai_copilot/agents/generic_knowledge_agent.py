"""Agent for general options and trading-psychology knowledge."""

from langchain_core.documents import Document

from trader_intelligence_ai_copilot.retrieval.base import BaseRetriever


class GenericKnowledgeAgent:
    """Retrieve education content without accessing trader-specific data."""

    _CATEGORIES = ("options", "trading_psychology")

    def __init__(self, retriever: BaseRetriever) -> None:
        self._retriever = retriever

    def retrieve(self, question: str, k_per_category: int = 3) -> list[Document]:
        """Retrieve and de-duplicate relevant options and psychology documents."""
        documents: list[Document] = []
        seen: set[tuple[str, str]] = set()

        for category in self._CATEGORIES:
            for document in self._retriever.retrieve(
                question,
                k=k_per_category,
                metadata_filter={"category": category},
            ):
                key = (document.page_content, str(document.metadata))
                if key not in seen:
                    seen.add(key)
                    documents.append(document)

        return documents
