from langchain_core.documents import Document
from dataclasses import dataclass
from time import perf_counter

from trader_intelligence_ai_copilot.retrieval.base import BaseRetriever
from trader_intelligence_ai_copilot.vectorstore.base import BaseVectorStore


@dataclass(frozen=True, slots=True)
class RetrievalDiagnostics:
    search_type: str
    metadata_filter: dict[str, str] | None
    document_count: int
    duration_ms: float


class VectorRetriever(BaseRetriever):
    """Retriever backed by a vector store."""

    def __init__(
        self,
        vector_store: BaseVectorStore,
    ) -> None:
        self._vector_store = vector_store
        self.last_diagnostics: RetrievalDiagnostics | None = None

    def retrieve(
        self,
        query: str,
        k: int = 5,
        metadata_filter: dict[str, str] | None = None,
        search_type: str = "similarity",
    ) -> list[Document]:
        started = perf_counter()
        if search_type == "mmr":
            documents = self._vector_store.max_marginal_relevance_search(
                query=query, k=k, fetch_k=max(k * 4, 20), metadata_filter=metadata_filter
            )
        elif search_type == "similarity":
            documents = self._vector_store.similarity_search(
                query=query, k=k, metadata_filter=metadata_filter
            )
        else:
            raise ValueError(f"Unsupported search type: {search_type}")
        self.last_diagnostics = RetrievalDiagnostics(
            search_type, metadata_filter, len(documents), (perf_counter() - started) * 1000
        )
        return documents
