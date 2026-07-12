from pydantic import Field

from trader_intelligence_ai_copilot.config.base import BaseConfig


class EmbeddingsConfig(BaseConfig):
    """Embedding configuration."""

    provider: str = Field(
        default="gemini",
        alias="EMBEDDING_PROVIDER",
    )

    model: str = Field(
        default="gemini-embedding-001",
        alias="EMBEDDING_MODEL",
    )