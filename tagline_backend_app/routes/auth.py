"""
auth.py

Authentication-related routes for the Tagline backend.
Includes /login (and /refresh in the future).
"""

from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from tagline_backend_app.auth_service import AuthService
from tagline_backend_app.config import get_settings
from tagline_backend_app.db import get_db
from tagline_backend_app.deps import get_token_store
from tagline_backend_app.schemas import (
    LoginRequest,
    RefreshRequest,
)

router = APIRouter()


@router.post("/logout", status_code=200)
def logout(response: Response):
    """
    Clear authentication cookies.

    Returns:
        JSON response indicating successful logout.
    """
    # Clear both access and refresh token cookies
    response.delete_cookie(key="tagline_access_token", path="/")
    response.delete_cookie(key="tagline_refresh_token", path="/")

    return {"detail": "Successfully logged out"}


@router.post("/refresh", status_code=200)
def refresh(
    response: Response,
    payload: Optional[RefreshRequest] = None,
    refresh_token: str = Cookie(None, alias="tagline_refresh_token"),
    db: Session = Depends(get_db),
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

    # Hybrid: use cookie if present, else request body
    token = refresh_token
    if not token and payload is not None:
        token = payload.refresh_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
        )
    try:
        access_token, new_refresh_token, expires_in, refresh_expires_in = (
            auth_service.refresh_tokens(token)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    # Set cookies for tokens
    settings = get_settings()
    response.set_cookie(
        key="tagline_access_token",
        value=access_token,
        max_age=expires_in,
        httponly=True,
        secure=False,  # Set to False for local testing over HTTP
        samesite="lax",  # Use 'strict' for maximum security, 'lax' for better UX
        path="/",
    )
    response.set_cookie(
        key="tagline_refresh_token",
        value=new_refresh_token,
        max_age=refresh_expires_in,
        httponly=True,
        secure=False,  # Set to False for local testing over HTTP
        samesite="lax",
        path="/",
    )

    # Return the response object directly after setting content
    response.status_code = status.HTTP_200_OK
    response.headers["Content-Type"] = "application/json"
    response.body = JSONResponse(
        content={"detail": "Token refreshed successfully"}
    ).body
    return response


@router.post("/login", status_code=200)
def login(
    response: Response,
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
    # Set cookies for tokens
    settings = get_settings()
    response.set_cookie(
        key="tagline_access_token",
        value=access_token,
        max_age=expires_in,
        httponly=True,
        secure=False,  # Set to False for local testing over HTTP
        samesite="lax",  # Use 'strict' for maximum security, 'lax' for better UX
        path="/",
    )
    response.set_cookie(
        key="tagline_refresh_token",
        value=refresh_token,
        max_age=refresh_expires_in,
        httponly=True,
        secure=False,  # Set to False for local testing over HTTP
        samesite="lax",
        path="/",
    )

    # Return the response object directly after setting content
    response.status_code = status.HTTP_200_OK
    response.headers["Content-Type"] = "application/json"
    response.body = JSONResponse(content={"detail": "Login successful"}).body
    return response
