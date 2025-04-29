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
        width: Image width in pixels (nullable for legacy rows)
        height: Image height in pixels (nullable for legacy rows)
        created_at: Timezone-aware timestamp when the photo was added (UTC)
        updated_at: Timezone-aware timestamp when the photo was last modified (UTC)
    """

    __tablename__ = "photos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(nullable=True)
    height: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
