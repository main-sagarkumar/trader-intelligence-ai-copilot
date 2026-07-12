from langchain_core.documents import Document

from trader_intelligence_ai_copilot.chat import (
    ContextBuilder,
)

def test_missing_metadata_defaults_to_unknown():
    document = Document(
        page_content="Hello",
        metadata={},
    )

    result = ContextBuilder.build_context([document])

    assert "Unknown" in result.context

    source = result.sources[0]

    assert source.document_name == "Unknown"
    assert source.category == "Unknown"