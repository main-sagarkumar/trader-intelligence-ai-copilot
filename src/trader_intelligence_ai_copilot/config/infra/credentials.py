from pydantic import Field, SecretStr

from trader_intelligence_ai_copilot.config.base import BaseConfig


class CredentialsConfig(BaseConfig):
    """External service credentials."""

    gemini_api_key: SecretStr = Field(
        default=SecretStr(""),
        alias="GEMINI_API_KEY",
    )

    openai_api_key: SecretStr = Field(
        default=SecretStr(""),
        alias="OPENAI_API_KEY",
    )