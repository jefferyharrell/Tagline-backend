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
from ..schemas import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=200)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
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
    auth_service = AuthService(settings, db)
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
