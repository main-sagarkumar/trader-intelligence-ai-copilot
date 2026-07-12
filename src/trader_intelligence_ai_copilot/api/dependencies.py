from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from trader_intelligence_ai_copilot.application.auth_service import AuthService
from trader_intelligence_ai_copilot.application.chat_service import ChatService
from trader_intelligence_ai_copilot.application.graph_chat_service import GraphChatService
from trader_intelligence_ai_copilot.application.memory_chat_service import MemoryChatService
from trader_intelligence_ai_copilot.agents import GenericKnowledgeAgent, TraderIntelligenceAgent
from trader_intelligence_ai_copilot.auth import AuthenticatedUser, InvalidTokenError, JWTService
from trader_intelligence_ai_copilot.orchestration import TraderGraph
from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.database.session import SessionLocal, get_engine
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.llm.factory import get_llm
from trader_intelligence_ai_copilot.knowledge.document_loader import DocumentLoader
from trader_intelligence_ai_copilot.knowledge.document_processor import DocumentProcessor
from trader_intelligence_ai_copilot.knowledge.ingest_service import IngestService
from trader_intelligence_ai_copilot.vectorstore.factory import get_vector_store
from trader_intelligence_ai_copilot.retrieval.factory import get_retriever
from trader_intelligence_ai_copilot.repositories.postgres_auth_repository import (
    PostgresAuthRepository,
)
from trader_intelligence_ai_copilot.repositories.postgres_trader_repository import (
    PostgresTraderRepository,
)
from trader_intelligence_ai_copilot.repositories.postgres_conversation_repository import (
    PostgresConversationRepository,
)

_bearer_scheme = HTTPBearer()

def get_llm_provider() -> BaseLLMProvider:
    return get_llm()


def get_db_session() -> Generator[Session, None, None]:
    """Yield a request-scoped database session."""
    with SessionLocal(bind=get_engine()) as session:
        yield session


def get_auth_service(
    session: Session = Depends(get_db_session),
) -> AuthService:
    """Build the local authentication service for one request."""
    security = get_settings().security
    return AuthService(
        repository=PostgresAuthRepository(session),
        jwt_service=JWTService(security),
        security=security,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    session: Session = Depends(get_db_session),
) -> AuthenticatedUser:
    """Validate an access token and load current roles and trader grants."""
    try:
        claims = JWTService(get_settings().security).decode_access_token(
            credentials.credentials
        )
        user = PostgresAuthRepository(session).get_user_by_id(
            UUID(str(claims["sub"]))
        )
    except (InvalidTokenError, KeyError, ValueError):
        user = None

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )
    return user


def get_hybrid_chat_service(
    session: Session = Depends(get_db_session),
) -> MemoryChatService:
    """Build a hybrid service with request-scoped database access."""
    trader_repository = PostgresTraderRepository(session)
    retriever = get_retriever()
    graph_service = GraphChatService(
        llm=get_llm_provider(),
        graph=TraderGraph(
            trader_agent=TraderIntelligenceAgent(trader_repository, retriever),
            generic_agent=GenericKnowledgeAgent(retriever),
        ),
    )
    return MemoryChatService(
        chat_service=graph_service,
        repository=PostgresConversationRepository(session),
    )


def get_chat_service() -> ChatService:
    return ChatService(
        llm=get_llm_provider(),
        retriever=get_retriever(),
    )


def get_ingest_service() -> IngestService:

    return IngestService(
        loader=DocumentLoader(),
        processor=DocumentProcessor(),
        vector_store=get_vector_store(),
    )
