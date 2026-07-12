from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.embeddings import Embeddings

from trader_intelligence_ai_copilot.config import get_settings
from trader_intelligence_ai_copilot.embeddings.base import BaseEmbeddingProvider


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Gemini embedding implementation."""

    def __init__(self) -> None:
        settings = get_settings()

        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.embeddings.model,
            api_key=settings.credentials.gemini_api_key,
        )

    def embed_documents(
        self,
        documents: list[Document],
    ) -> list[list[float]]:

        texts = [
            document.page_content
            for document in documents
        ]

        return self._embeddings.embed_documents(texts)

    def embed_query(
        self,
        text: str,
    ) -> list[float]:

        return self._embeddings.embed_query(text)
    
    def embedding_function(
        self,
    ) -> Embeddings:
        """Return the LangChain embedding implementation."""
        return self._embeddings