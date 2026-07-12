"""Graph-backed application service for personalized chat."""

from trader_intelligence_ai_copilot.chat import ChatResult, ContextBuilder, HybridContext
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.orchestration import TraderGraph
from trader_intelligence_ai_copilot.prompts import HybridRAGPromptBuilder
from trader_intelligence_ai_copilot.observability import metrics
from trader_intelligence_ai_copilot.observability.events import log_event


class GraphChatService:
    """Generate grounded responses from LangGraph-routed agent context."""

    def __init__(self, graph: TraderGraph, llm: BaseLLMProvider) -> None:
        self._graph = graph
        self._llm = llm

    async def chat(
        self,
        question: str,
        trader_id: str,
        conversation_history: str = "",
        retrieval_query: str | None = None,
    ) -> ChatResult:
        """Run authorized agent retrieval, merge context, and generate an answer."""
        with metrics.timer("retrieval_duration_ms"):
            state = self._graph.invoke(retrieval_query or question, trader_id)
        documents = [
            *state.get("trader_documents", []),
            *state.get("generic_documents", []),
        ]
        context_result = ContextBuilder.build_context(documents)
        context = HybridContext(
            user_question=question,
            trader_profile=state.get("trader_profile"),
            retrieved_documents=documents,
            knowledge_context=context_result.context,
            sources=context_result.sources,
            conversation_history=conversation_history,
        )
        prompt = HybridRAGPromptBuilder.build_prompt_value(context)
        with metrics.timer("llm_duration_ms"):
            answer = await self._llm.generate_response(prompt.to_messages())
        log_event(
            "ai_route_completed",
            route=state.get("route", "unknown"),
            document_count=len(documents),
            categories=sorted(
                {str(document.metadata.get("category", "unknown")) for document in documents}
            ),
        )
        return ChatResult(answer=answer, sources=context.sources)
