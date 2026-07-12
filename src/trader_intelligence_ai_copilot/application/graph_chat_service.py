"""Graph-backed application service for personalized chat."""

from trader_intelligence_ai_copilot.chat import ChatResult, ContextBuilder, HybridContext
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.orchestration import TraderGraph
from trader_intelligence_ai_copilot.prompts import HybridRAGPromptBuilder


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
        answer = await self._llm.generate_response(prompt.to_messages())
        return ChatResult(answer=answer, sources=context.sources)
