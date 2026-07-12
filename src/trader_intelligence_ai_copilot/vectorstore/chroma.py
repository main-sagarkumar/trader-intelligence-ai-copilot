from langchain_chroma import Chroma
from langchain_core.documents import Document

from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.embeddings.factory import (
    get_embedding_provider,
)
from trader_intelligence_ai_copilot.vectorstore.base import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    """Chroma vector store implementation."""

    def __init__(self) -> None:
        settings = get_settings()

        embedding_provider = get_embedding_provider()

        self._vector_store = Chroma(
            collection_name=settings.vectorstore.collection_name,
            persist_directory=settings.vectorstore.persist_directory,
            embedding_function=embedding_provider.embedding_function(),
        )

    def add_documents(
        self,
        documents: list[Document],
    ) -> None:
        self._vector_store.add_documents(documents)

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[Document]:
        return self._vector_store.similarity_search(
            query=query,
            k=k,
            filter=metadata_filter,
        )

    def reset(self) -> None:
        self._vector_store.reset_collection()
