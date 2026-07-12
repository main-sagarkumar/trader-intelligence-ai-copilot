"""Tests for diverse, filtered, conversation-aware retrieval."""

from langchain_core.documents import Document

from trader_intelligence_ai_copilot.chat import ContextBuilder
from trader_intelligence_ai_copilot.retrieval.query_rewriter import (
    ConversationQueryRewriter,
)
from trader_intelligence_ai_copilot.retrieval.vector_retriever import VectorRetriever


class FakeVectorStore:
    def __init__(self) -> None:
        self.call = None

    def max_marginal_relevance_search(
        self, query, k=5, fetch_k=20, metadata_filter=None
    ):
        self.call = (query, k, fetch_k, metadata_filter)
        return [Document(page_content="Diverse guidance")]


def test_mmr_preserves_metadata_filter_and_diagnostics() -> None:
    store = FakeVectorStore()
    retriever = VectorRetriever(store)

    documents = retriever.retrieve(
        "cluster guidance",
        k=3,
        metadata_filter={"category": "trader_intelligence"},
        search_type="mmr",
    )

    assert len(documents) == 1
    assert store.call == (
        "cluster guidance",
        3,
        20,
        {"category": "trader_intelligence"},
    )
    assert retriever.last_diagnostics is not None
    assert retriever.last_diagnostics.document_count == 1


def test_follow_up_query_uses_previous_user_question() -> None:
    rewritten = ConversationQueryRewriter.rewrite(
        "How can I improve?",
        "user: Why am I Cluster 3?\nassistant: Your leverage is elevated.",
        "TRADER_101",
    )

    assert "TRADER_101" in rewritten
    assert "Why am I Cluster 3?" in rewritten
    assert "How can I improve?" in rewritten


def test_context_deduplicates_document_page_sources() -> None:
    metadata = {
        "document_name": "guide.pdf",
        "category": "trader_intelligence",
        "page": 3,
        "relative_path": "trader_intelligence/guide.pdf",
    }
    result = ContextBuilder.build_context(
        [
            Document(page_content="First chunk", metadata=metadata),
            Document(page_content="Duplicate page chunk", metadata=metadata),
        ]
    )

    assert len(result.sources) == 1
    assert "Duplicate page chunk" not in result.context
