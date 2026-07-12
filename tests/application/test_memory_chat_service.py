"""Tests for ownership-safe bounded conversation memory."""

import asyncio
from uuid import UUID, uuid4

import pytest

from trader_intelligence_ai_copilot.application.memory_chat_service import (
    ConversationAccessError,
    MemoryChatService,
)
from trader_intelligence_ai_copilot.chat import ChatResult, SourceReference
from trader_intelligence_ai_copilot.memory import ConversationMessage, ConversationSession


USER_ID = UUID("00000000-0000-0000-0000-000000000001")


class FakeConversationRepository:
    def __init__(self) -> None:
        self.session = ConversationSession(uuid4(), USER_ID, "TRADER_101")
        self.messages = [ConversationMessage("user", "Why am I Cluster 3?")]

    def create_session(self, user_id, trader_id):
        self.session = ConversationSession(self.session.id, user_id, trader_id)
        return self.session

    def get_owned_session(self, session_id, user_id):
        if session_id == self.session.id and user_id == self.session.user_id:
            return self.session
        return None

    def add_message(self, session_id, role, content):
        self.messages.append(ConversationMessage(role, content))

    def recent_messages(self, session_id, limit=8):
        return self.messages[-limit:]

    def commit(self):
        pass


class FakeGraphService:
    def __init__(self) -> None:
        self.history = ""

    async def chat(
        self, question, trader_id, conversation_history="", retrieval_query=None
    ):
        self.history = conversation_history
        self.retrieval_query = retrieval_query
        return ChatResult(
            "Use lower leverage.",
            [SourceReference("guide.pdf", "trader_intelligence", 1, "guide.pdf")],
        )


def test_follow_up_uses_history_and_persists_turn() -> None:
    repository = FakeConversationRepository()
    graph = FakeGraphService()
    service = MemoryChatService(graph, repository)

    result = asyncio.run(
        service.chat("How can I improve?", "TRADER_101", USER_ID, repository.session.id)
    )

    assert "Why am I Cluster 3?" in graph.history
    assert "Previous question: Why am I Cluster 3?" in graph.retrieval_query
    assert result.session_id == repository.session.id
    assert [message.role for message in repository.messages[-2:]] == ["user", "assistant"]


def test_rejects_session_owned_by_another_user() -> None:
    repository = FakeConversationRepository()
    service = MemoryChatService(FakeGraphService(), repository)

    with pytest.raises(ConversationAccessError):
        asyncio.run(
            service.chat(
                "Continue", "TRADER_101", uuid4(), repository.session.id
            )
        )


def test_pii_is_redacted_before_memory_and_model() -> None:
    repository = FakeConversationRepository()
    graph = FakeGraphService()
    service = MemoryChatService(graph, repository)

    asyncio.run(
        service.chat(
            "My email is trader@example.com. How can I improve?",
            "TRADER_101",
            USER_ID,
        )
    )

    stored_question = repository.messages[-2].content
    assert "trader@example.com" not in stored_question
    assert "[REDACTED_EMAIL]" in stored_question
    assert "trader@example.com" not in graph.retrieval_query
