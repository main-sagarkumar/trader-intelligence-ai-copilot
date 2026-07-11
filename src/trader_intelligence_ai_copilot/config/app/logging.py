from enum import Enum

from pydantic import Field

from trader_intelligence_ai_copilot.config.base import BaseConfig


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingConfig(BaseConfig):
    """Logging configuration."""

    level: LogLevel = Field(
        default=LogLevel.INFO,
        alias="LOG_LEVEL",
    )

    json_logs: bool = Field(
        default=False,
        alias="JSON_LOGS",
    )