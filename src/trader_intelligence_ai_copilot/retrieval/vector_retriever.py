from langchain_core.documents import Document

from trader_intelligence_ai_copilot.retrieval.base import BaseRetriever
from trader_intelligence_ai_copilot.vectorstore.base import BaseVectorStore


class VectorRetriever(BaseRetriever):
    """Retriever backed by a vector store."""

    def __init__(
        self,
        vector_store: BaseVectorStore,
    ) -> None:
        self._vector_store = vector_store

    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> list[Document]:

        return self._vector_store.similarity_search(
            query=query,
            k=k,
        )