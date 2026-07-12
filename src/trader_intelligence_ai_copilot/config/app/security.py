from pydantic import Field, SecretStr

from trader_intelligence_ai_copilot.config.base import BaseConfig


class SecurityConfig(BaseConfig):
    """Security configuration."""

    jwt_secret_key: SecretStr = Field(
        default=SecretStr(""),
        alias="JWT_SECRET_KEY",
    )

    algorithm: str = Field(
        default="HS256",
        alias="JWT_ALGORITHM",
    )

    access_token_expire_minutes: int = Field(
        default=60,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    refresh_token_expire_days: int = Field(
        default=7,
        alias="REFRESH_TOKEN_EXPIRE_DAYS",
    )

    jwt_issuer: str = Field(
        default="trader-intelligence-ai-copilot",
        alias="JWT_ISSUER",
    )

    jwt_audience: str = Field(
        default="trader-intelligence-ai-copilot-api",
        alias="JWT_AUDIENCE",
    )
