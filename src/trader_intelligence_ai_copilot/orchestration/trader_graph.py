"""LangGraph routing for specialized trader and generic knowledge agents."""

from typing import Literal, NotRequired, Protocol, TypedDict, cast

from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph

from trader_intelligence_ai_copilot.trader import TraderProfile


class TraderAgent(Protocol):
    """Structural contract for trader-intelligence retrieval."""

    def retrieve(
        self,
        question: str,
        trader_id: str,
    ) -> tuple[TraderProfile | None, list[Document]]: ...


class GenericAgent(Protocol):
    """Structural contract for generic knowledge retrieval."""

    def retrieve(self, question: str) -> list[Document]: ...


class TraderGraphState(TypedDict):
    """State shared by the controlled agent-routing workflow."""

    question: str
    trader_id: str
    route: NotRequired[Literal["trader", "generic", "both"]]
    trader_profile: NotRequired[TraderProfile | None]
    trader_documents: NotRequired[list[Document]]
    generic_documents: NotRequired[list[Document]]


class TraderGraph:
    """Route questions to authorized trader and generic knowledge agents."""

    def __init__(
        self,
        trader_agent: TraderAgent,
        generic_agent: GenericAgent,
    ) -> None:
        self._trader_agent = trader_agent
        self._generic_agent = generic_agent
        self._graph = self._build()

    def invoke(self, question: str, trader_id: str) -> TraderGraphState:
        """Run the graph for a trader ID already authorized by the API layer."""
        return cast(
            TraderGraphState,
            self._graph.invoke({"question": question, "trader_id": trader_id}),
        )

    def _build(self):
        graph = StateGraph(TraderGraphState)
        graph.add_node("route", self._route)
        graph.add_node("trader", self._trader)
        graph.add_node("generic", self._generic)
        graph.add_edge(START, "route")
        graph.add_conditional_edges("route", self._next, {"trader": "trader", "generic": "generic", "both": "trader"})
        graph.add_conditional_edges("trader", self._after_trader, {"generic": "generic", "end": END})
        graph.add_edge("generic", END)
        return graph.compile()

    def _route(self, state: TraderGraphState) -> dict[str, object]:
        question = state["question"].lower()
        trader_terms = ("my ", "cluster", "profile", "improve", "leverage", "pnl")
        generic_terms = ("option", "volatility", "psychology", "revenge", "emotion")
        has_trader = any(term in question for term in trader_terms)
        has_generic = any(term in question for term in generic_terms)
        route: Literal["trader", "generic", "both"] = "both" if has_trader and has_generic else "trader" if has_trader else "generic"
        return {"route": route}

    def _next(self, state: TraderGraphState) -> Literal["trader", "generic", "both"]:
        route = state.get("route")
        if route is None:
            raise RuntimeError("Graph route was not set before conditional routing.")

        return route

    def _after_trader(self, state: TraderGraphState) -> Literal["generic", "end"]:
        route = state.get("route")
        if route is None:
            raise RuntimeError("Graph route was not set before conditional routing.")

        return "generic" if route == "both" else "end"

    def _trader(self, state: TraderGraphState) -> dict[str, object]:
        profile, documents = self._trader_agent.retrieve(state["question"], state["trader_id"])
        return {"trader_profile": profile, "trader_documents": documents}

    def _generic(self, state: TraderGraphState) -> dict[str, object]:
        return {"generic_documents": self._generic_agent.retrieve(state["question"])}
