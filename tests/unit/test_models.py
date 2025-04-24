"""
test_models.py

Unit tests for SQLAlchemy ORM models in Tagline backend.
Focus: Photo model field defaults, nullability, and DB integration.
"""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Photo


def test_photo_instantiation_defaults(db_session: Session) -> None:
    photo = Photo(filename="test.jpg")
    db_session.add(photo)
    db_session.flush()  # Assign defaults
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


def test_photo_filename_required(db_session: Session) -> None:
    photo = Photo()  # type: ignore[call-arg]
    db_session.add(photo)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_photo_db_integration(db_session: Session) -> None:
    photo = Photo(filename="dbtest.jpg", description="desc")
    db_session.add(photo)
    db_session.commit()
    retrieved = db_session.query(Photo).filter_by(filename="dbtest.jpg").first()  # type: ignore[call-arg]
    assert retrieved is not None
    assert retrieved.filename == "dbtest.jpg"
    assert retrieved.description == "desc"
    assert isinstance(retrieved.id, uuid.UUID)
    assert isinstance(retrieved.created_at, datetime)
    assert isinstance(retrieved.updated_at, datetime)
