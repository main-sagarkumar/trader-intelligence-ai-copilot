from trader_intelligence_ai_copilot.chat import (
    ChatResult,
    ContextBuilder,
)
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.prompts import RAGPromptBuilder
from trader_intelligence_ai_copilot.retrieval.base import BaseRetriever


class ChatService:
    """Application service for Retrieval-Augmented Generation."""

    def __init__(
        self,
        llm: BaseLLMProvider,
        retriever: BaseRetriever,
    ) -> None:
        self._llm = llm
        self._retriever = retriever

        # Prompt template is immutable, so build it once.
        self._prompt = RAGPromptBuilder.build()

    async def chat(
        self,
        question: str,
    ) -> ChatResult:
        """
        Generate a grounded response using Retrieval-Augmented Generation.
        """

        # Retrieve relevant documents.
        documents = self._retriever.retrieve(question)

        # Build formatted context.
        context_result = ContextBuilder.build_context(
            documents,
        )

        # Build prompt.
        prompt_value = self._prompt.invoke(
            {
                "context": context_result.context,
                "question": question,
            }
        )

        # Generate response.
        answer = await self._llm.generate_response(
            prompt_value.to_messages(),
        )

        return ChatResult(
            answer=answer,
            sources=context_result.sources,
        )