from abc import ABC, abstractmethod

from langchain_core.documents import Document


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_documents(
        self,
        documents: list[Document],
    ) -> list[list[float]]:
        """Generate embeddings for multiple documents."""
        ...

    @abstractmethod
    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        """Generate an embedding for a search query."""
        ...