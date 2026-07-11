from pydantic import Field, SecretStr

from trader_intelligence_ai_copilot.config.base import BaseConfig
from trader_intelligence_ai_copilot.config.enums.providers import DatabaseProvider


class DatabaseConfig(BaseConfig):
    """Database configuration."""

    provider: DatabaseProvider = Field(
        default=DatabaseProvider.POSTGRES,
        alias="DATABASE_PROVIDER",
    )

    url: SecretStr = Field(
        default=SecretStr(""),
        alias="DATABASE_URL",
    )

    echo: bool = Field(
        default=False,
        alias="DATABASE_ECHO",
    )

    pool_size: int = Field(
        default=10,
        alias="DATABASE_POOL_SIZE",
    )