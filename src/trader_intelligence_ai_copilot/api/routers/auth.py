"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from trader_intelligence_ai_copilot.application.auth_service import AuthService, AuthenticationError
from trader_intelligence_ai_copilot.api.dependencies import get_auth_service
from trader_intelligence_ai_copilot.auth import InvalidTokenError
from trader_intelligence_ai_copilot.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Authenticate a local user and return access and refresh tokens."""
    try:
        tokens = service.login(request.email, request.password)
    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.") from error

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshTokenRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Rotate a valid refresh token and return a new token pair."""
    try:
        tokens = service.refresh(request.refresh_token)
    except (AuthenticationError, InvalidTokenError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.") from error

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> None:
    """Revoke a refresh token and end the associated refresh session."""
    try:
        service.logout(request.refresh_token)
    except (AuthenticationError, InvalidTokenError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        ) from error
