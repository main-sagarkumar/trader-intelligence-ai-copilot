"""Privacy-safe request correlation context."""

from contextvars import ContextVar, Token
from hashlib import sha256
from uuid import UUID


request_id_context: ContextVar[str] = ContextVar("request_id", default="unknown")


def set_request_id(request_id: str) -> Token[str]:
    return request_id_context.set(request_id)


def reset_request_id(token: Token[str]) -> None:
    request_id_context.reset(token)


def anonymous_user_id(user_id: UUID) -> str:
    """Return a stable, non-reversible identifier safe for telemetry."""
    return sha256(str(user_id).encode("utf-8")).hexdigest()[:16]
