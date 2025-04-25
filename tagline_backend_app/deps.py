"""
deps.py

Dependency injection helpers for FastAPI.
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from tagline_backend_app.auth_service import AuthService
from tagline_backend_app.config import get_settings

security = HTTPBearer()


def get_token_store(request: Request):
    return request.app.state.token_store


def get_current_user(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Dependency to require a valid access token via Authorization header."""
    settings = get_settings()
    token_store = get_token_store(request)
    auth_service = AuthService(settings, token_store)
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    claims = auth_service.validate_token(token, token_type="access")
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return claims
