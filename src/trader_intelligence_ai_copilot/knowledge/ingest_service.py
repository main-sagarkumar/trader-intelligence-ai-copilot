import math
import time
from pathlib import Path

from trader_intelligence_ai_copilot.knowledge.document_loader import (
    DocumentLoader,
)
from trader_intelligence_ai_copilot.knowledge.document_processor import (
    DocumentProcessor,
)
from trader_intelligence_ai_copilot.vectorstore.base import BaseVectorStore

# TODO: Move these to config later if required.
BATCH_SIZE = 90
WAIT_TIME = 60  # seconds


class IngestService:
    """Knowledge ingestion service."""

    def __init__(
        self,
        loader: DocumentLoader,
        processor: DocumentProcessor,
        vector_store: BaseVectorStore,
    ) -> None:
        self._loader = loader
        self._processor = processor
        self._vector_store = vector_store

    def ingest(
        self,
        documents_path: Path,
    ) -> None:
        """Execute the complete knowledge ingestion pipeline."""

        print("=" * 60)
        print("Trader Intelligence AI Copilot")
        print("Knowledge Ingestion Pipeline")
        print("=" * 60)

        # ----------------------------------------------------
        # Load Documents
        # ----------------------------------------------------
        print("\nLoading documents...\n")

        documents = self._loader.load_documents(
            documents_path,
        )

        print(f"Loaded {len(documents)} pages")

        # ----------------------------------------------------
        # Split Documents
        # ----------------------------------------------------
        print("\nSplitting documents...\n")

        chunks = self._processor.split_documents(
            documents,
        )

        print(f"Generated {len(chunks)} chunks")

        # ----------------------------------------------------
        # Reset Vector Store
        # ----------------------------------------------------
        print("\nResetting vector store...\n")

        self._vector_store.reset()

        # ----------------------------------------------------
        # Store Chunks
        # ----------------------------------------------------
        print("Saving documents...\n")

        total_chunks = len(chunks)
        total_batches = math.ceil(total_chunks / BATCH_SIZE)

        for batch_number, start in enumerate(
            range(0, total_chunks, BATCH_SIZE),
            start=1,
        ):
            end = min(start + BATCH_SIZE, total_chunks)

            batch = chunks[start:end]

            print(
                f"Batch {batch_number}/{total_batches}"
            )

            self._vector_store.add_documents(batch)

            print(
                f"Stored {end}/{total_chunks} chunks"
            )

            if batch_number < total_batches:
                print(
                    f"Waiting {WAIT_TIME} seconds...\n"
                )
                time.sleep(WAIT_TIME)

        print("\n" + "=" * 60)
        print("Knowledge ingestion completed successfully!")
        print("=" * 60)