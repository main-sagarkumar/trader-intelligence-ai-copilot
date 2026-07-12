"""Models returned by hybrid context assembly."""

from pydantic import BaseModel, ConfigDict
from langchain_core.documents import Document

from trader_intelligence_ai_copilot.chat.context_models import SourceReference
from trader_intelligence_ai_copilot.trader import TraderProfile


class HybridContext(BaseModel):
    """Structured trader and knowledge context for prompt construction."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    user_question: str
    trader_profile: TraderProfile | None
    retrieved_documents: list[Document]
    knowledge_context: str
    sources: list[SourceReference]
    conversation_history: str = ""
