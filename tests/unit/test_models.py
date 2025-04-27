"""
Unit tests for tagline_backend_app.models.Photo
Covers: Instantiation, field defaults, constraints (in-memory SQLite DB)
"""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from tagline_backend_app.models import Base, Photo

pytestmark = pytest.mark.unit


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False, future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_photo_instantiation_defaults(db_session):
    photo = Photo(filename="cat.jpg")
    db_session.add(photo)
    db_session.commit()
    db_session.refresh(photo)
    # UUID primary key
    assert isinstance(photo.id, uuid.UUID)
    # Required fields
    assert photo.filename == "cat.jpg"
    # Optional field
    assert photo.description is None
    # created_at and updated_at are set to UTC datetimes
    assert isinstance(photo.created_at, datetime)
    # SQLite does not preserve tzinfo; accept naive or UTC-aware
    if photo.created_at.tzinfo is None:
        # Should be naive UTC
        assert photo.created_at.utcoffset() is None
    else:
        assert photo.created_at.tzinfo.utcoffset(
            photo.created_at
        ) == timezone.utc.utcoffset(photo.created_at)
    assert isinstance(photo.updated_at, datetime)
    if photo.updated_at.tzinfo is None:
        assert photo.updated_at.utcoffset() is None
    else:
        assert photo.updated_at.tzinfo.utcoffset(
            photo.updated_at
        ) == timezone.utc.utcoffset(photo.updated_at)


def test_photo_constraints(db_session):
    # filename is required
    with pytest.raises(Exception):
        db_session.add(Photo())
        db_session.commit()
    db_session.rollback()  # Required after IntegrityError before next transaction
    # description is optional
    photo = Photo(filename="dog.jpg", description="A dog.")
    db_session.add(photo)
    db_session.commit()
    db_session.refresh(photo)
    assert photo.description == "A dog."


def test_photo_table_schema(db_session):
    inspector = inspect(db_session.get_bind())
    columns = {col["name"]: col for col in inspector.get_columns("photos")}
    assert "id" in columns and columns["id"]["primary_key"]
    assert columns["filename"]["nullable"] is False
    assert columns["description"]["nullable"] is True
    assert columns["created_at"]["nullable"] is False
    assert columns["updated_at"]["nullable"] is False
