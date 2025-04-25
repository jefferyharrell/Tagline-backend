"""
schemas.py

Pydantic models for authentication endpoints (login, tokens).
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request payload for /login endpoint."""

    password: str = Field(..., description="The backend password.")


class LoginResponse(BaseModel):
    """Response payload for /login endpoint."""

    access_token: str = Field(..., description="JWT access token.")
    refresh_token: str = Field(..., description="JWT refresh token.")
    token_type: str = Field("bearer", description="Token type (usually 'bearer').")
    expires_in: int = Field(..., description="Access token expiration time in seconds.")
    refresh_expires_in: int = Field(
        ..., description="Refresh token expiration time in seconds."
    )


class RefreshRequest(BaseModel):
    """Request payload for /refresh endpoint."""

    refresh_token: str = Field(
        ..., description="The refresh token to exchange for a new access token."
    )


class RefreshResponse(BaseModel):
    """Response payload for /refresh endpoint."""

    access_token: str = Field(..., description="New JWT access token.")
    refresh_token: str = Field(..., description="New JWT refresh token.")
    token_type: str = Field("bearer", description="Token type (usually 'bearer').")
    expires_in: int = Field(..., description="Access token expiration time in seconds.")
    refresh_expires_in: int = Field(
        ..., description="Refresh token expiration time in seconds."
    )


class PhotoMetadata(BaseModel):
    """Metadata for a single photo in list responses."""

    id: str
    filename: str
    description: str | None = None
    created_at: str
    updated_at: str


class PhotoListResponse(BaseModel):
    """Paginated list of photos."""

    total: int
    limit: int
    offset: int
    items: list[PhotoMetadata]


# Optionally, we could define error response models here as well if desired.
