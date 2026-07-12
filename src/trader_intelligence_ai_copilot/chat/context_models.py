from dataclasses import dataclass, field


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

@dataclass(frozen=True, slots=True)
class ChatResult:
    """Result returned by the ChatService."""

    answer: str
    sources: list[SourceReference]
    retrieved_contexts: tuple[str, ...] = ()
    trader_facts: dict[str, str | int | float | None] = field(default_factory=dict)
