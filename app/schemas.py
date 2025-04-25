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


class PhotoMetadataFields(BaseModel):
    """Extensible metadata fields for a photo (spec-compliant)."""

    description: str | None = None  # Required for MVP, add more fields as needed


class Photo(BaseModel):
    """Canonical Photo object for both single-photo and list responses (spec-compliant)."""

    id: str = Field(..., description="Unique photo ID (UUID)")
    object_key: str = Field(
        ..., description="Storage path/object key for the photo blob"
    )
    metadata: PhotoMetadataFields = Field(
        ..., description="Dictionary of metadata fields (at minimum: description)"
    )
    last_modified: str = Field(
        ..., description="RFC3339/ISO8601 last modified timestamp"
    )


class PhotoListResponse(BaseModel):
    """Paginated list of photos (spec-compliant)."""

    total: int
    limit: int
    offset: int
    items: list[Photo]
