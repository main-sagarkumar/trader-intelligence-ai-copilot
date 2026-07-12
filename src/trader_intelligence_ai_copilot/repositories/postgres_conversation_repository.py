"""PostgreSQL conversation-memory repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from trader_intelligence_ai_copilot.database.models import (
    ChatMessageModel,
    ChatSessionModel,
)
from trader_intelligence_ai_copilot.memory.models import (
    ConversationMessage,
    ConversationSession,
)
from trader_intelligence_ai_copilot.repositories.conversation_repository import (
    ConversationRepository,
)


class PostgresConversationRepository(ConversationRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_session(self, user_id: UUID, trader_id: str) -> ConversationSession:
        model = ChatSessionModel(user_id=user_id, trader_id=trader_id)
        self._session.add(model)
        self._session.flush()
        return ConversationSession(model.id, model.user_id, model.trader_id)

    def get_owned_session(
        self, session_id: UUID, user_id: UUID
    ) -> ConversationSession | None:
        model = self._session.scalar(
            select(ChatSessionModel).where(
                ChatSessionModel.id == session_id,
                ChatSessionModel.user_id == user_id,
            )
        )
        if model is None:
            return None
        return ConversationSession(model.id, model.user_id, model.trader_id)

    def add_message(self, session_id: UUID, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError("Conversation role must be user or assistant.")
        self._session.add(
            ChatMessageModel(session_id=session_id, role=role, content=content)
        )
        self._session.flush()

    def recent_messages(
        self, session_id: UUID, limit: int = 8
    ) -> list[ConversationMessage]:
        rows = list(
            self._session.scalars(
                select(ChatMessageModel)
                .where(ChatMessageModel.session_id == session_id)
                .order_by(ChatMessageModel.created_at.desc(), ChatMessageModel.id.desc())
                .limit(limit)
            )
        )
        return [ConversationMessage(row.role, row.content) for row in reversed(rows)]

    def commit(self) -> None:
        """Atomically persist the completed user/assistant turn."""
        self._session.commit()
