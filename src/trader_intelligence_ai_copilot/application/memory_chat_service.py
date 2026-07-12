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


class ConversationAccessError(Exception):
    """Raised when a conversation is missing or belongs to another user."""


@dataclass(frozen=True, slots=True)
class MemoryChatResult:
    session_id: UUID
    answer: str
    sources: list[SourceReference]


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
        self._repository.add_message(conversation.id, "user", question)
        retrieval_query = ConversationQueryRewriter.rewrite(
            question, formatted_history, trader_id
        )
        result = await self._chat_service.chat(
            question,
            trader_id,
            conversation_history=formatted_history,
            retrieval_query=retrieval_query,
        )
        self._repository.add_message(conversation.id, "assistant", result.answer)
        self._repository.commit()
        return MemoryChatResult(conversation.id, result.answer, result.sources)
