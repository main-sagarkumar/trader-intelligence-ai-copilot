"""Authentication API request and response schemas."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials submitted to create an application session."""

    email: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1)


class RefreshTokenRequest(BaseModel):
    """Refresh token submitted to rotate a user session."""

    refresh_token: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Signed tokens returned after authentication or refresh."""

    access_token: str
    refresh_token: str
    token_type: str
