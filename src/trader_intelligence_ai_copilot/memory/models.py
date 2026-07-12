"""Conversation-memory domain models."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class ConversationSession:
    id: UUID
    user_id: UUID
    trader_id: str
