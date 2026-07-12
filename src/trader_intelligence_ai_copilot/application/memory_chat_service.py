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
from trader_intelligence_ai_copilot.observability import anonymous_user_id, metrics
from trader_intelligence_ai_copilot.observability.events import log_event


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
        with metrics.timer("input_guardrail_duration_ms"):
            input_result = InputGuardrail.evaluate(question)
        if not input_result.allowed:
            metrics.increment("guardrail_blocks_total")
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
        metrics.increment("memory_messages_loaded_total", len(history))
        formatted_history = "\n".join(
            f"{message.role}: {message.content}" for message in history
        )
        self._repository.add_message(conversation.id, "user", safe_question)
        if input_result.intervention_response is not None:
            metrics.increment("guardrail_interventions_total")
            answer = input_result.intervention_response
            self._repository.add_message(conversation.id, "assistant", answer)
            self._repository.commit()
            log_event(
                "personalized_chat_completed",
                user=anonymous_user_id(user_id),
                session_id=str(conversation.id),
                guardrail_reasons=input_result.reasons,
                source_count=0,
            )
            return MemoryChatResult(
                conversation.id, answer, [], input_result.reasons
            )

        retrieval_query = ConversationQueryRewriter.rewrite(
            safe_question, formatted_history, trader_id
        )
        with metrics.timer("ai_pipeline_duration_ms"):
            result = await self._chat_service.chat(
                safe_question,
                trader_id,
                conversation_history=formatted_history,
                retrieval_query=retrieval_query,
            )
        with metrics.timer("output_guardrail_duration_ms"):
            output_result = OutputGuardrail.evaluate(
                result.answer, trader_id, has_sources=bool(result.sources)
            )
        if output_result.reasons:
            metrics.increment("guardrail_interventions_total")
        safe_answer = output_result.text
        self._repository.add_message(conversation.id, "assistant", safe_answer)
        self._repository.commit()
        metrics.increment("retrieved_documents_total", len(result.sources))
        log_event(
            "personalized_chat_completed",
            user=anonymous_user_id(user_id),
            session_id=str(conversation.id),
            guardrail_reasons=(*input_result.reasons, *output_result.reasons),
            source_count=len(result.sources),
        )
        return MemoryChatResult(
            conversation.id,
            safe_answer,
            result.sources if output_result.allowed else [],
            (*input_result.reasons, *output_result.reasons),
        )
