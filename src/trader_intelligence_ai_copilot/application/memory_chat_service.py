"""Personalized chat orchestration with ownership-safe bounded memory."""

from dataclasses import dataclass
from uuid import UUID

from trader_intelligence_ai_copilot.application.graph_chat_service import GraphChatService
from trader_intelligence_ai_copilot.chat import SourceReference
from trader_intelligence_ai_copilot.repositories.conversation_repository import (
    ConversationRepository,
)
from trader_intelligence_ai_copilot.retrieval.query_rewriter import (
    ConversationQueryRewriter,
)
from trader_intelligence_ai_copilot.guardrails import InputGuardrail, OutputGuardrail


class ConversationAccessError(Exception):
    """Raised when a conversation is missing or belongs to another user."""


class GuardrailViolation(Exception):
    """Raised when unsafe input must not enter the AI workflow."""


@dataclass(frozen=True, slots=True)
class MemoryChatResult:
    session_id: UUID
    answer: str
    sources: list[SourceReference]
    guardrail_reasons: tuple[str, ...] = ()


class MemoryChatService:
    def __init__(
        self,
        chat_service: GraphChatService,
        repository: ConversationRepository,
        history_limit: int = 8,
    ) -> None:
        self._chat_service = chat_service
        self._repository = repository
        self._history_limit = history_limit

    async def chat(
        self,
        question: str,
        trader_id: str,
        user_id: UUID,
        session_id: UUID | None = None,
    ) -> MemoryChatResult:
        input_result = InputGuardrail.evaluate(question)
        if not input_result.allowed:
            raise GuardrailViolation(",".join(input_result.reasons))
        safe_question = input_result.text

        if session_id is None:
            conversation = self._repository.create_session(user_id, trader_id)
        else:
            conversation = self._repository.get_owned_session(session_id, user_id)
            if conversation is None or conversation.trader_id != trader_id:
                raise ConversationAccessError("Conversation is not accessible.")

        history = self._repository.recent_messages(
            conversation.id, self._history_limit
        )
        formatted_history = "\n".join(
            f"{message.role}: {message.content}" for message in history
        )
        self._repository.add_message(conversation.id, "user", safe_question)
        if input_result.intervention_response is not None:
            answer = input_result.intervention_response
            self._repository.add_message(conversation.id, "assistant", answer)
            self._repository.commit()
            return MemoryChatResult(
                conversation.id, answer, [], input_result.reasons
            )

        retrieval_query = ConversationQueryRewriter.rewrite(
            safe_question, formatted_history, trader_id
        )
        result = await self._chat_service.chat(
            safe_question,
            trader_id,
            conversation_history=formatted_history,
            retrieval_query=retrieval_query,
        )
        output_result = OutputGuardrail.evaluate(
            result.answer, trader_id, has_sources=bool(result.sources)
        )
        safe_answer = output_result.text
        self._repository.add_message(conversation.id, "assistant", safe_answer)
        self._repository.commit()
        return MemoryChatResult(
            conversation.id,
            safe_answer,
            result.sources if output_result.allowed else [],
            (*input_result.reasons, *output_result.reasons),
        )
