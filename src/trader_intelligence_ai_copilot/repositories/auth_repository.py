"""Authentication repository contract."""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from trader_intelligence_ai_copilot.auth.models import AuthenticatedUser, RefreshTokenRecord


class AuthRepository(ABC):
    """Interface for local identity and authorization data."""

    @abstractmethod
    def get_user_by_email(self, email: str) -> AuthenticatedUser | None: ...

    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> AuthenticatedUser | None: ...

    @abstractmethod
    def create_refresh_token(self, record: RefreshTokenRecord) -> None: ...

    @abstractmethod
    def get_refresh_token(self, token_hash: str) -> RefreshTokenRecord | None: ...

    @abstractmethod
    def revoke_refresh_token(self, token_id: UUID, revoked_at: datetime) -> None: ...
