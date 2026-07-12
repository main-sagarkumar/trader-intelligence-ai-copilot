"""Tests for hybrid context assembly."""

from langchain_core.documents import Document

from trader_intelligence_ai_copilot.chat import HybridContextBuilder
from trader_intelligence_ai_copilot.repositories.trader_repository import TraderRepository
from trader_intelligence_ai_copilot.retrieval.base import BaseRetriever
from trader_intelligence_ai_copilot.trader import TraderProfile


class FakeTraderRepository(TraderRepository):
    """In-memory trader repository for unit tests."""

    def __init__(self, profile: TraderProfile | None) -> None:
        self.profile = profile
        self.requested_trader_id: str | None = None

    def get_by_id(self, trader_id: str) -> TraderProfile | None:
        self.requested_trader_id = trader_id
        return self.profile


class FakeRetriever(BaseRetriever):
    """Static document retriever for unit tests."""

    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents
        self.query: str | None = None
        self.k: int | None = None

    def retrieve(self, query: str, k: int = 5) -> list[Document]:
        self.query = query
        self.k = k
        return self.documents


def make_profile() -> TraderProfile:
    """Build a representative trader profile."""
    return TraderProfile(
        trader_id="TRADER_101",
        persona="spread_trader",
        account_size=100_000,
        final_balance=105_000.0,
        total_trades=95,
        total_pnl=5_000.0,
        avg_pnl=52.63,
        win_rate=0.61,
        avg_holding_minutes=120.0,
        avg_leverage=2.5,
        avg_risk_pct=0.02,
        stop_loss_usage_rate=0.8,
        overnight_position_rate=0.3,
        roi_pct=0.05,
        cluster=3,
    )


def test_build_combines_trader_profile_and_knowledge_documents() -> None:
    """Builder should retain structured and unstructured context separately."""
    document = Document(
        page_content="Stop-loss rules limit downside risk.",
        metadata={
            "document_name": "risk_guide.pdf",
            "category": "risk_management",
            "page": 4,
            "relative_path": "risk/risk_guide.pdf",
        },
    )
    repository = FakeTraderRepository(make_profile())
    retriever = FakeRetriever([document])
    builder = HybridContextBuilder(repository, retriever)

    result = builder.build(
        question="Why should I use a stop-loss?",
        trader_id="TRADER_101",
        k=3,
    )

    assert result.user_question == "Why should I use a stop-loss?"
    assert result.trader_profile == make_profile()
    assert result.retrieved_documents == [document]
    assert "Stop-loss rules limit downside risk." in result.knowledge_context
    assert len(result.sources) == 1
    assert repository.requested_trader_id == "TRADER_101"
    assert retriever.query == "Why should I use a stop-loss?"
    assert retriever.k == 3


def test_build_returns_empty_knowledge_context_when_no_documents_found() -> None:
    """Builder should still return a profile when retrieval has no matches."""
    builder = HybridContextBuilder(
        FakeTraderRepository(make_profile()),
        FakeRetriever([]),
    )

    result = builder.build("Explain my profile.", "TRADER_101")

    assert result.trader_profile is not None
    assert result.knowledge_context == ""
    assert result.sources == []


def test_build_allows_missing_trader_profile() -> None:
    """Builder should represent a missing trader without failing retrieval."""
    builder = HybridContextBuilder(
        FakeTraderRepository(None),
        FakeRetriever([]),
    )

    result = builder.build("Explain my profile.", "UNKNOWN")

    assert result.trader_profile is None
