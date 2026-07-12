"""Prompt construction for personalized hybrid RAG responses."""

from dataclasses import fields

from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import ChatPromptTemplate

from trader_intelligence_ai_copilot.chat.hybrid_context_models import HybridContext
from trader_intelligence_ai_copilot.trader import TraderProfile


class HybridRAGPromptBuilder:
    """Build prompts from structured trader data and knowledge context."""

    _MISSING_PROFILE_CONTEXT = "No trader profile was found for this request."

    @staticmethod
    def build() -> ChatPromptTemplate:
        """Build the immutable hybrid RAG prompt template."""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are Trader Intelligence AI Copilot.

Use the structured trader profile and knowledge context provided by the
application to answer the user's question. The application, not you,
retrieves all data.

Guidelines:

1. Use only the supplied trader profile and knowledge context.
2. Clearly distinguish trader-specific facts from general knowledge.
3. Do not infer, calculate, or invent missing trader metrics.
4. If a trader profile is unavailable, say that personalized analysis is not
   available and answer only from the knowledge context when possible.
5. If the supplied context does not answer the question, clearly say so.
6. Be clear, concise, professional, and educational.
""",
                ),
                (
                    "human",
                    """
Trader Profile:

{trader_context}

Knowledge Context:

{knowledge_context}

Recent Conversation History:

{conversation_history}

Question:

{question}
""",
                ),
            ]
        )

    @classmethod
    def build_prompt_value(cls, context: HybridContext) -> PromptValue:
        """Render a hybrid context object into an LLM-ready prompt value."""
        return cls.build().invoke(
            {
                "trader_context": cls._format_trader_profile(
                    context.trader_profile
                ),
                "knowledge_context": context.knowledge_context,
                "conversation_history": context.conversation_history or "No previous messages.",
                "question": context.user_question,
            }
        )

    @classmethod
    def _format_trader_profile(cls, profile: TraderProfile | None) -> str:
        """Format structured trader metrics without adding derived claims."""
        if profile is None:
            return cls._MISSING_PROFILE_CONTEXT

        return "\n".join(
            f"{field.name}: {getattr(profile, field.name)}"
            for field in fields(profile)
        )
