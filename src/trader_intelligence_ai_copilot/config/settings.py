from functools import lru_cache

from trader_intelligence_ai_copilot.config.app.application import ApplicationConfig
from trader_intelligence_ai_copilot.config.app.logging import LoggingConfig
from trader_intelligence_ai_copilot.config.app.security import SecurityConfig
from trader_intelligence_ai_copilot.config.infra.credentials import CredentialsConfig
from trader_intelligence_ai_copilot.config.infra.database import DatabaseConfig
from trader_intelligence_ai_copilot.config.infra.llm import LLMConfig

class ApplicationSettings:

    def __init__(self):
        self.app = ApplicationConfig()
        self.logging = LoggingConfig()
        self.security = SecurityConfig()
        self.database = DatabaseConfig()
        self.credentials = CredentialsConfig()
        self.llm = LLMConfig()


@lru_cache
def get_settings() -> ApplicationSettings:
    return ApplicationSettings()