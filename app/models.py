"""
models.py

SQLAlchemy ORM models for Tagline backend.
Defines the Photo table with metadata fields as required by the project spec.
"""

import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Photo(Base):
    """
    Photo table storing metadata for each uploaded photo.

    Attributes:
        id: Unique identifier (UUID, primary key)
        filename: Name of the photo file
        description: Optional description of the photo
        created_at: Timezone-aware timestamp when the photo was added (UTC)
        updated_at: Timezone-aware timestamp when the photo was last modified (UTC)
    """

    __tablename__ = "photos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class RefreshToken(Base):
    """
    RefreshToken table for storing issued refresh tokens and their revocation status.

    Attributes:
        id: Unique identifier (UUID, primary key)
        token: The refresh token string (or its hash)
        issued_at: Timezone-aware timestamp when the token was issued (UTC)
        expires_at: Timezone-aware timestamp when the token expires (UTC)
        revoked: Boolean flag indicating if the token is revoked
        revoked_at: Timezone-aware timestamp when the token was revoked (nullable)
        last_used_at: Timezone-aware timestamp when the token was last used (nullable)
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(default=False, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
