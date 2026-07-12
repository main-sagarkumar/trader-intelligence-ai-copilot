"""Persistence contract for conversation memory."""

from abc import ABC, abstractmethod
from uuid import UUID

from trader_intelligence_ai_copilot.memory.models import (
    ConversationMessage,
    ConversationSession,
)


class ConversationRepository(ABC):
    @abstractmethod
    def create_session(self, user_id: UUID, trader_id: str) -> ConversationSession: ...

    @abstractmethod
    def get_owned_session(
        self, session_id: UUID, user_id: UUID
    ) -> ConversationSession | None: ...

    @abstractmethod
    def add_message(self, session_id: UUID, role: str, content: str) -> None: ...

    @abstractmethod
    def recent_messages(
        self, session_id: UUID, limit: int = 8
    ) -> list[ConversationMessage]: ...

    @abstractmethod
    def commit(self) -> None: ...
