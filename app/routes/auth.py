"""
auth.py

Authentication-related routes for the Tagline backend.
Includes /login (and /refresh in the future).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth_service import AuthService
from ..config import get_settings
from ..db import get_db
from ..deps import get_token_store
from ..schemas import LoginRequest, LoginResponse, RefreshRequest, RefreshResponse

router = APIRouter()


@router.post("/refresh", response_model=RefreshResponse, status_code=200)
def refresh(
    payload: RefreshRequest,
    db: Session = Depends(get_db),  # DB used only for unrelated features
    token_store=Depends(get_token_store),
):
    """
    Exchange a refresh token for new access and refresh tokens.

    Args:
        payload (RefreshRequest): The refresh request payload.
        db (Session): SQLAlchemy DB session (injected).
    Returns:
        RefreshResponse: New tokens if refresh succeeds.
    Raises:
        HTTPException: 401 if refresh token is invalid/expired/revoked.
    """
    settings = get_settings()
    auth_service = AuthService(settings, token_store)
    try:
        access_token, refresh_token, expires_in, refresh_expires_in = (
            auth_service.refresh_tokens(payload.refresh_token)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc
    return RefreshResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        refresh_expires_in=refresh_expires_in,
    )


@router.post("/login", response_model=LoginResponse, status_code=200)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),  # DB used only for unrelated features
    token_store=Depends(get_token_store),
):
    """
    Authenticate user with password and issue access/refresh tokens.

    Args:
        payload (LoginRequest): The login request payload (password).
        db (Session): SQLAlchemy DB session (injected).
    Returns:
        LoginResponse: Access and refresh tokens if authentication succeeds.
    Raises:
        HTTPException: 401 if password is invalid.
    """
    settings = get_settings()
    auth_service = AuthService(settings, token_store)
    if not auth_service.verify_password(payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    access_token, refresh_token, expires_in, refresh_expires_in = (
        auth_service.issue_tokens()
    )
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        refresh_expires_in=refresh_expires_in,
    )
