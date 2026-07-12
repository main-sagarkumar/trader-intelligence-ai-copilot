from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Chat request."""

    question: str


class SourceResponse(BaseModel):
    """Knowledge source used to generate the answer."""

    document_name: str
    category: str
    page: int | str
    relative_path: str


class ChatResponse(BaseModel):
    """Chat response."""

    answer: str
    sources: list[SourceResponse]