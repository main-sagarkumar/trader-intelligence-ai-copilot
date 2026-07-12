from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from trader_intelligence_ai_copilot.config import get_settings


class DocumentProcessor:
    """Splits enterprise documents into chunks."""

    def __init__(self) -> None:

        settings = get_settings()

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.embeddings.chunk_size,
            chunk_overlap=settings.embeddings.chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    def split_documents(
        self,
        documents: list[Document],
    ) -> list[Document]:

        return self._splitter.split_documents(documents)