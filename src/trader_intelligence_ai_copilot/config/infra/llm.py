from pydantic import Field

from trader_intelligence_ai_copilot.config.base import BaseConfig
from trader_intelligence_ai_copilot.config.enums.providers import LLMProvider


class LLMConfig(BaseConfig):
    """LLM configuration."""

    provider: LLMProvider = Field(
        default=LLMProvider.GEMINI,
        alias="LLM_PROVIDER",
    )

    model: str = Field(
        default="gemini-flash-latest",
        alias="LLM_MODEL",
    )

    temperature: float = Field(
        default=0.2,
        alias="LLM_TEMPERATURE",
    )

    max_tokens: int = Field(
        default=2048,
        alias="LLM_MAX_TOKENS",
    )

    timeout: int = Field(
        default=60,
        alias="LLM_TIMEOUT",
    )