from pydantic import Field

from trader_intelligence_ai_copilot.config.base import BaseConfig


class VectorStoreConfig(BaseConfig):
    """Vector store configuration."""

    provider: str = Field(
        default="chroma",
        alias="VECTOR_STORE_PROVIDER",
    )

    persist_directory: str = Field(
        default="data/chroma",
        alias="CHROMA_PERSIST_DIRECTORY",
    )

    collection_name: str = Field(
        default="trader_knowledge",
        alias="CHROMA_COLLECTION_NAME",
    )