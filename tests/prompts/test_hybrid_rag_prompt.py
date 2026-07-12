"""Tests for the hybrid RAG prompt builder."""

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from trader_intelligence_ai_copilot.chat.hybrid_context_models import HybridContext
from trader_intelligence_ai_copilot.prompts import HybridRAGPromptBuilder
from trader_intelligence_ai_copilot.trader import TraderProfile


def make_profile() -> TraderProfile:
    """Build a representative profile for prompt tests."""
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


def make_context(profile: TraderProfile | None) -> HybridContext:
    """Build hybrid context for prompt tests."""
    return HybridContext(
        user_question="Why am I in this cluster?",
        trader_profile=profile,
        retrieved_documents=[Document(page_content="Cluster guidance.")],
        knowledge_context="Cluster 3 has moderate risk behaviour.",
        sources=[],
    )


def test_build_returns_chat_prompt_template() -> None:
    """Builder should return a LangChain prompt template."""
    assert isinstance(HybridRAGPromptBuilder.build(), ChatPromptTemplate)


def test_build_prompt_value_includes_profile_knowledge_and_question() -> None:
    """Prompt should contain both structured and unstructured context."""
    prompt_value = HybridRAGPromptBuilder.build_prompt_value(
        make_context(make_profile())
    )
    human_message = prompt_value.to_messages()[1].content

    assert "trader_id: TRADER_101" in human_message
    assert "cluster: 3" in human_message
    assert "Cluster 3 has moderate risk behaviour." in human_message
    assert "Why am I in this cluster?" in human_message


def test_build_prompt_value_marks_missing_profile() -> None:
    """Prompt should explicitly represent missing trader data."""
    prompt_value = HybridRAGPromptBuilder.build_prompt_value(make_context(None))

    assert (
        "No trader profile was found for this request."
        in prompt_value.to_messages()[1].content
    )
