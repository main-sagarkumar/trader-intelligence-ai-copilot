"""Password hashing and verification."""

from passlib.context import CryptContext

_PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    """Hash and verify passwords without exposing hashing details to callers."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Return a bcrypt hash for a non-empty password."""
        if not password:
            raise ValueError("Password must not be empty.")

        return _PASSWORD_CONTEXT.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Return whether a password matches its stored hash."""
        return _PASSWORD_CONTEXT.verify(password, password_hash)
