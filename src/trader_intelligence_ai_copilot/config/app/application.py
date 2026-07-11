from pydantic import Field

from trader_intelligence_ai_copilot.config.base import BaseConfig
from trader_intelligence_ai_copilot.config.enums.environment import Environment


class ApplicationConfig(BaseConfig):
    """Application configuration."""

    name: str = Field(
        default="Trader Intelligence AI Copilot",
        alias="APP_NAME",
    )

    version: str = Field(
        default="0.1.0",
        alias="APP_VERSION",
    )

    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        alias="ENVIRONMENT",
    )

    debug: bool = Field(
        default=False,
        alias="DEBUG",
    )