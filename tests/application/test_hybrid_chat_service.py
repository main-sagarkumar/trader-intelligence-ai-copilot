"""Tests for the hybrid chat application service."""

import asyncio
from collections.abc import Sequence

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

from trader_intelligence_ai_copilot.application import HybridChatService
from trader_intelligence_ai_copilot.chat import HybridContextBuilder
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.repositories.trader_repository import TraderRepository
from trader_intelligence_ai_copilot.retrieval.base import BaseRetriever
from trader_intelligence_ai_copilot.trader import TraderProfile


class FakeLLMProvider(BaseLLMProvider):
    """LLM provider that captures prompt messages for testing."""

    def __init__(self) -> None:
        self.messages: Sequence[BaseMessage] | None = None

    async def generate_response(self, messages: Sequence[BaseMessage]) -> str:
        self.messages = messages
        return "Personalized response"


class FakeTraderRepository(TraderRepository):
    """Repository that returns a fixed trader profile."""

    def get_by_id(self, trader_id: str) -> TraderProfile | None:
        return TraderProfile(
            trader_id=trader_id,
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


class FakeRetriever(BaseRetriever):
    """Retriever that returns one grounded document."""

    def retrieve(self, query: str, k: int = 5) -> list[Document]:
        return [
            Document(
                page_content="Cluster 3 guidance.",
                metadata={
                    "document_name": "cluster_guide.pdf",
                    "category": "trader_intelligence",
                    "page": 3,
                    "relative_path": "trader_intelligence/cluster_guide.pdf",
                },
            )
        ]


def test_chat_generates_answer_from_hybrid_context() -> None:
    """Service should pass trader metrics and knowledge to the LLM."""
    llm = FakeLLMProvider()
    service = HybridChatService(
        llm=llm,
        context_builder=HybridContextBuilder(
            trader_repository=FakeTraderRepository(),
            retriever=FakeRetriever(),
        ),
    )

    result = asyncio.run(service.chat("Why am I Cluster 3?", "TRADER_101"))

    assert result.answer == "Personalized response"
    assert len(result.sources) == 1
    assert llm.messages is not None
    human_message = llm.messages[1].content
    assert "trader_id: TRADER_101" in human_message
    assert "cluster: 3" in human_message
    assert "Cluster 3 guidance." in human_message
