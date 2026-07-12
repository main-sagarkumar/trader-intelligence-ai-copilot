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
    ) -> list[Document]:
        """Retrieve similar documents."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Delete all stored documents."""
        ...