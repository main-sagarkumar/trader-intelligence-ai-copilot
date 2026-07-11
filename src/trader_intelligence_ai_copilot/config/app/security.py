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