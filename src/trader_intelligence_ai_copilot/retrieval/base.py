from abc import ABC, abstractmethod

from langchain_core.documents import Document


class BaseRetriever(ABC):
    """Abstract base class for document retrieval."""

    @abstractmethod
    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> list[Document]:
        """Retrieve relevant documents."""
        ...