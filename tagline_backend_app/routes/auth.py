"""
auth.py

Authentication-related routes for the Tagline backend.
Includes /login (and /refresh in the future).
"""

import logging
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
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
from tagline_backend_app.token_store import TokenStore

# Get logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/logout", status_code=200)
def logout(
    response: Response,
    request: Request,
    token_store: Annotated[TokenStore, Depends(get_token_store)],
    refresh_token: Annotated[str | None, Cookie(alias="tagline_refresh_token")] = None,
):
    """
    Revoke the refresh token in the TokenStore and clear authentication cookies.

    Args:
        response: The FastAPI Response object.
        request: The FastAPI Request object.
        token_store: The TokenStore dependency.
        refresh_token: The refresh token extracted from the cookie.

    Returns:
        JSON response indicating successful logout.
    """
    # Revoke the refresh token if it exists
    if refresh_token:
        try:
            token_store.revoke_refresh_token(refresh_token)
        except Exception as e:
            # Log the error, but proceed with cookie deletion
            # Consider if specific exceptions should be handled differently
            print(f"Error revoking token during logout: {e}")  # Basic logging

    # Clear both access and refresh token cookies
    response.delete_cookie(
        key="tagline_access_token", path="/", httponly=True, samesite="lax"
    )
    response.delete_cookie(
        key="tagline_refresh_token", path="/", httponly=True, samesite="lax"
    )  # Use the actual cookie name

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
        logger.warning("Refresh attempt failed: No refresh token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
        )
    try:
        access_token, new_refresh_token, expires_in, refresh_expires_in = (
            auth_service.refresh_tokens(token)
        )
    except Exception:
        logger.warning("Refresh attempt failed: Invalid or expired refresh token")
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
    logger.info("Token refresh successful")
    return response


@router.post("/login", status_code=200)
def login(
    response: Response,
    payload: LoginRequest,
    db: Session = Depends(get_db),
    token_store=Depends(get_token_store),
):
    # Add explicit type logging to help debug test issues
    import inspect

    logger.debug(f"ROUTE /login: token_store type = {type(token_store).__name__}")
    module = inspect.getmodule(token_store)
    module_name = module.__name__ if module is not None else "<unknown>"
    logger.debug(f"ROUTE /login: token_store module = {module_name}")
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
    logger.debug(f"ROUTE /login: Received token_store dependency: {token_store}")
    settings = get_settings()
    auth_service = AuthService(settings, token_store)
    logger.debug(
        f"ROUTE /login: Created auth_service with store: {auth_service.token_store}"
    )
    if not auth_service.verify_password(payload.password):
        logger.warning("Login attempt failed: Invalid password")
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
    logger.info("Login successful")
    return response
