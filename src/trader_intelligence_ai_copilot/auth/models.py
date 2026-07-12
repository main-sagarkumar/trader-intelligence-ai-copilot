"""Domain models for authentication and authorization."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """Authenticated local user and their effective access grants."""

    id: UUID
    email: str
    password_hash: str
    is_active: bool
    roles: frozenset[str]
    trader_ids: frozenset[str]


@dataclass(frozen=True, slots=True)
class TokenPair:
    """Access and refresh tokens issued after successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(frozen=True, slots=True)
class RefreshTokenRecord:
    """Persisted lifecycle state for a hashed refresh token."""

    id: UUID
    user_id: UUID
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None
