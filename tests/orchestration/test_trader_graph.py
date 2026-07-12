"""Tests for LangGraph agent routing."""

from langchain_core.documents import Document

from trader_intelligence_ai_copilot.orchestration import TraderGraph


class FakeTraderAgent:
    """Captures trader-agent calls without external dependencies."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def retrieve(self, question: str, trader_id: str):
        self.calls.append((question, trader_id))
        return None, [Document(page_content="Trader intelligence")]


class FakeGenericAgent:
    """Captures generic-agent calls without external dependencies."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def retrieve(self, question: str):
        self.calls.append(question)
        return [Document(page_content="Generic knowledge")]


def build_graph() -> tuple[TraderGraph, FakeTraderAgent, FakeGenericAgent]:
    """Build a graph with inspectable fake agent dependencies."""
    trader = FakeTraderAgent()
    generic = FakeGenericAgent()
    return TraderGraph(trader, generic), trader, generic


def test_routes_trader_question_to_trader_agent() -> None:
    graph, trader, generic = build_graph()

    result = graph.invoke("Why am I Cluster 3?", "TRADER_101")

    assert result.get("route") == "trader"
    assert trader.calls == [("Why am I Cluster 3?", "TRADER_101")]
    assert generic.calls == []


def test_routes_generic_question_to_generic_agent() -> None:
    graph, trader, generic = build_graph()

    result = graph.invoke("What is implied volatility?", "TRADER_101")

    assert result.get("route") == "generic"
    assert trader.calls == []
    assert generic.calls == ["What is implied volatility?"]


def test_routes_combined_question_to_both_agents() -> None:
    graph, trader, generic = build_graph()

    result = graph.invoke(
        "How does my leverage affect my options strategy?",
        "TRADER_101",
    )

    assert result.get("route") == "both"
    assert len(trader.calls) == 1
    assert len(generic.calls) == 1
