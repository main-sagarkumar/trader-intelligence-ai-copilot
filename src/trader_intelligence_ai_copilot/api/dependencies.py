from trader_intelligence_ai_copilot.application.chat_service import ChatService
from trader_intelligence_ai_copilot.llm.base import BaseLLMProvider
from trader_intelligence_ai_copilot.llm.factory import get_llm
from trader_intelligence_ai_copilot.knowledge.document_loader import DocumentLoader
from trader_intelligence_ai_copilot.knowledge.document_processor import DocumentProcessor
from trader_intelligence_ai_copilot.knowledge.ingest_service import IngestService
from trader_intelligence_ai_copilot.vectorstore.factory import get_vector_store
from trader_intelligence_ai_copilot.retrieval.factory import get_retriever



def get_llm_provider() -> BaseLLMProvider:
    return get_llm()


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