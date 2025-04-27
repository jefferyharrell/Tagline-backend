"""
deps.py

Dependency injection helpers for FastAPI.
"""

from typing import Optional

from fastapi import Cookie, HTTPException, Request, status

from tagline_backend_app.auth_service import AuthService
from tagline_backend_app.config import get_settings


def get_token_store(request: Request):
    return request.app.state.token_store


def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(None, alias="tagline_access_token"),
):
    """Dependency to require a valid access token via the 'tagline_access_token' cookie only."""
    settings = get_settings()
    token_store = get_token_store(request)
    auth_service = AuthService(settings, token_store)

    token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    claims = auth_service.validate_token(token, token_type="access")
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return claims
