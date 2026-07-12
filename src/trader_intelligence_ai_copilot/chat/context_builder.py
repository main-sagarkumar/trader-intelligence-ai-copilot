from langchain_core.documents import Document

from trader_intelligence_ai_copilot.chat.context_models import (
    ContextResult,
    SourceReference,
)


class ContextBuilder:
    """Builds LLM context from retrieved documents."""

    SEPARATOR = "\n\n" + ("-" * 80) + "\n\n"

    UNKNOWN = "Unknown"

    HEADER_TEMPLATE = (
    "Source: {document_name}\n"
    "Category: {category}\n"
    "Page: {page}\n"
    "Path: {relative_path}\n\n"
    )

    @classmethod
    def build_context(
        cls,
        documents: list[Document],
    ) -> ContextResult:
        """Build formatted context and source references."""

        if not documents:
            return ContextResult(
                context="",
                sources=[],
            )

        sections: list[str] = []
        sources: list[SourceReference] = []

        for document in documents:
            metadata = document.metadata

            source = SourceReference(
                document_name=metadata.get(
                    "document_name",
                    cls.UNKNOWN,
                ),
                category=metadata.get(
                    "category",
                    cls.UNKNOWN,
                ),
                page=metadata.get(
                    "page",
                    cls.UNKNOWN,
                ),
                relative_path=metadata.get(
                    "relative_path",
                    cls.UNKNOWN,
                ),
            )

            sources.append(source)

            header = cls.HEADER_TEMPLATE.format(
                document_name=source.document_name,
                category=source.category,
                page=source.page,
                relative_path=source.relative_path,
            )

            section = header + document.page_content.strip()

            sections.append(section)
            
        context = cls.SEPARATOR.join(sections)

        return ContextResult(
            context=context,
            sources=sources,
        )