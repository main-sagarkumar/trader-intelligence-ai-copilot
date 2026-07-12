"""API-level tests for personalized chat authorization and response shaping."""

from uuid import UUID

from fastapi.testclient import TestClient

from trader_intelligence_ai_copilot.api.dependencies import (
    get_current_user,
    get_hybrid_chat_service,
)
from trader_intelligence_ai_copilot.api.main import app
from trader_intelligence_ai_copilot.auth import AuthenticatedUser
from trader_intelligence_ai_copilot.chat import SourceReference
from trader_intelligence_ai_copilot.application.memory_chat_service import MemoryChatResult


class FakeGraphChatService:
    async def chat(self, question, trader_id, user_id, session_id=None):
        return MemoryChatResult(
            session_id=UUID("00000000-0000-0000-0000-000000000099"),
            answer=f"Personalized answer for {trader_id}: {question}",
            sources=[SourceReference("guide.pdf", "trader_intelligence", 2, "guide.pdf")],
        )


def user_with_access() -> AuthenticatedUser:
    return AuthenticatedUser(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        email="trader_101@traders.local",
        password_hash="unused",
        is_active=True,
        roles=frozenset({"trader"}),
        trader_ids=frozenset({"TRADER_101"}),
    )


def test_authorized_personalized_chat_returns_sources() -> None:
    app.dependency_overrides[get_current_user] = user_with_access
    app.dependency_overrides[get_hybrid_chat_service] = FakeGraphChatService
    try:
        response = TestClient(app).post(
            "/chat/personalized",
            json={"question": "Why am I Cluster 3?", "trader_id": "TRADER_101"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["session_id"] == "00000000-0000-0000-0000-000000000099"
    assert response.json()["sources"][0]["document_name"] == "guide.pdf"


def test_personalized_chat_rejects_unassigned_trader() -> None:
    app.dependency_overrides[get_current_user] = user_with_access
    app.dependency_overrides[get_hybrid_chat_service] = FakeGraphChatService
    try:
        response = TestClient(app).post(
            "/chat/personalized",
            json={"question": "Show my profile", "trader_id": "TRADER_205"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
