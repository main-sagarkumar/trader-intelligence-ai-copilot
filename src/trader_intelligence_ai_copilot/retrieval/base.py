from abc import ABC, abstractmethod

from langchain_core.documents import Document


class BaseRetriever(ABC):
    """Abstract base class for document retrieval."""

    @abstractmethod
    def retrieve(
        self,
        query: str,
        k: int = 5,
        metadata_filter: dict[str, str] | None = None,
        search_type: str = "similarity",
    ) -> list[Document]:
        """Retrieve relevant documents."""
        ...
