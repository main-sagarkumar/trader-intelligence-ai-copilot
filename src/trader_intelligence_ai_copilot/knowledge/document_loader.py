from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class DocumentLoader:
    """Loads PDF documents recursively from a directory."""

    def load_documents(
        self,
        directory: Path,
    ) -> list[Document]:
        """
        Load all PDF documents recursively.

        Args:
            directory: Root directory containing PDF documents.

        Returns:
            List of LangChain Document objects.
        """

        if not directory.exists():
            raise FileNotFoundError(
                f"Directory not found: {directory}"
            )

        pdf_files = sorted(directory.rglob("*.pdf"))

        if not pdf_files:
            raise ValueError(
                f"No PDF files found in {directory}"
            )

        documents: list[Document] = []

        for pdf_file in pdf_files:

            print(f"Loading: {pdf_file.relative_to(directory)}")

            loader = PyPDFLoader(str(pdf_file))

            loaded_documents = loader.load()

            for document in loaded_documents:
                document.metadata["document_name"] = pdf_file.name
                document.metadata["category"] = pdf_file.parent.name
                document.metadata = {
                    "source": str(pdf_file),
                    "document_name": pdf_file.name,
                    "category": pdf_file.parent.name,
                    "relative_path": str(pdf_file.relative_to(directory)),
                    "page": document.metadata.get("page", 0),
                    "total_pages": document.metadata.get("total_pages"),
                    }

            documents.extend(loaded_documents)

        return documents