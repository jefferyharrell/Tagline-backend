"""
test_models.py

Unit tests for SQLAlchemy ORM models in Tagline backend.
Focus: Photo model field defaults, nullability, and DB integration.
"""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Photo


def test_photo_instantiation_defaults(in_memory_db: Session) -> None:
    photo = Photo(filename="test.jpg")
    in_memory_db.add(photo)
    in_memory_db.flush()  # Assign defaults
    assert isinstance(photo.id, uuid.UUID)
    assert photo.filename == "test.jpg"
    assert photo.description is None
    assert isinstance(photo.created_at, datetime)
    assert isinstance(photo.updated_at, datetime)
    # created_at and updated_at should be close to now (timezone-aware)
    now = datetime.now(photo.created_at.tzinfo)
    assert abs((now - photo.created_at).total_seconds()) < 2
    assert abs((now - photo.updated_at).total_seconds()) < 2


def test_photo_description_nullable() -> None:
    photo = Photo(filename="foo.jpg", description=None)
    assert photo.description is None


def test_photo_filename_required(in_memory_db: Session) -> None:
    photo = Photo()  # type: ignore[call-arg]
    in_memory_db.add(photo)
    with pytest.raises(IntegrityError):
        in_memory_db.commit()


def test_photo_db_integration(in_memory_db: Session) -> None:
    photo = Photo(filename="dbtest.jpg", description="desc")
    in_memory_db.add(photo)
    in_memory_db.commit()
    retrieved = in_memory_db.query(Photo).filter_by(filename="dbtest.jpg").first()  # type: ignore[call-arg]
    assert retrieved is not None
    assert retrieved.filename == "dbtest.jpg"
    assert retrieved.description == "desc"
    assert isinstance(retrieved.id, uuid.UUID)
    assert isinstance(retrieved.created_at, datetime)
    assert isinstance(retrieved.updated_at, datetime)
