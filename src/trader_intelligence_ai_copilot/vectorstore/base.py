from abc import ABC, abstractmethod

from langchain_core.documents import Document


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add_documents(
        self,
        documents: list[Document],
    ) -> None:
        """Store documents in the vector database."""
        ...

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[Document]:
        """Retrieve similar documents."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Delete all stored documents."""
        ...

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        metadata_filter: dict[str, str] | None = None,
    ) -> list[Document]:
        """Retrieve diverse documents, falling back to similarity search."""
        return self.similarity_search(query, k, metadata_filter)
