"""Application service for personalized hybrid RAG responses."""

from trader_intelligence_ai_copilot.chat import (
    ChatResult,
    HybridContextBuilder,
)
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.prompts import HybridRAGPromptBuilder


class HybridChatService:
    """Generate personalized responses from hybrid trader and knowledge context."""

    def __init__(
        self,
        llm: BaseLLMProvider,
        context_builder: HybridContextBuilder,
    ) -> None:
        """Initialize the service with an LLM and hybrid context builder."""
        self._llm = llm
        self._context_builder = context_builder

    async def chat(
        self,
        question: str,
        trader_id: str,
    ) -> ChatResult:
        """Generate a grounded, trader-specific response for a trusted identity."""
        context = self._context_builder.build(
            question=question,
            trader_id=trader_id,
        )
        prompt_value = HybridRAGPromptBuilder.build_prompt_value(context)
        answer = await self._llm.generate_response(prompt_value.to_messages())

        return ChatResult(
            answer=answer,
            sources=context.sources,
        )
