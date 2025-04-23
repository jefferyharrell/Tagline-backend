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

from app.models import Photo, RefreshToken


def test_refresh_token_instantiation_defaults(db_session: Session) -> None:
    token_str = "s3cr3t"
    expires = datetime.now().replace(microsecond=0)
    refresh_token = RefreshToken(token=token_str, expires_at=expires)
    db_session.add(refresh_token)
    db_session.flush()
    assert isinstance(refresh_token.id, uuid.UUID)
    assert refresh_token.token == token_str
    assert isinstance(refresh_token.issued_at, datetime)
    assert refresh_token.expires_at == expires
    assert refresh_token.revoked is False
    assert refresh_token.revoked_at is None
    assert refresh_token.last_used_at is None


def test_refresh_token_revocation_fields(db_session: Session) -> None:
    token_str = "revoke-me"
    expires = datetime.now().replace(microsecond=0)
    revoked_time = datetime.now().replace(microsecond=0)
    last_used = datetime.now().replace(microsecond=0)
    refresh_token = RefreshToken(
        token=token_str,
        expires_at=expires,
        revoked=True,
        revoked_at=revoked_time,
        last_used_at=last_used,
    )
    db_session.add(refresh_token)
    db_session.commit()
    retrieved = db_session.query(RefreshToken).filter_by(token=token_str).first()  # type: ignore[call-arg]
    assert retrieved is not None
    assert retrieved.revoked is True
    assert retrieved.revoked_at == revoked_time
    assert retrieved.last_used_at == last_used


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
