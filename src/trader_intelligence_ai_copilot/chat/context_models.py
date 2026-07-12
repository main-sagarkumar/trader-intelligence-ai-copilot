from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceReference:
    """Represents a retrieved knowledge source."""

    document_name: str
    category: str
    page: int | str
    relative_path: str


@dataclass(frozen=True, slots=True)
class ContextResult:
    """Result produced by the ContextBuilder."""

    context: str
    sources: list[SourceReference]