"""
Unit tests for tagline_backend_app.schemas Pydantic models.
"""
import pytest

pytestmark = pytest.mark.unit
from pydantic import ValidationError
from tagline_backend_app import schemas

def test_login_request_valid():
    req = schemas.LoginRequest(password="hunter2")
    assert req.password == "hunter2"

def test_login_request_missing_password():
    with pytest.raises(ValidationError):
        schemas.LoginRequest()

def test_login_response_fields():
    resp = schemas.LoginResponse(
        access_token="abc123",
        refresh_token="def456",
        expires_in=3600,
        refresh_expires_in=7200,
    )
    assert resp.access_token == "abc123"
    assert resp.refresh_token == "def456"
    assert resp.token_type == "bearer"
    assert resp.expires_in == 3600
    assert resp.refresh_expires_in == 7200

def test_photo_metadata_fields_optional():
    meta = schemas.PhotoMetadataFields()
    assert meta.description is None
    meta2 = schemas.PhotoMetadataFields(description="A nice photo!")
    assert meta2.description == "A nice photo!"

def test_photo_model_valid():
    meta = schemas.PhotoMetadataFields(description="desc")
    photo = schemas.Photo(
        id="uuid-1234",
        object_key="photos/uuid-1234.jpg",
        metadata=meta,
        last_modified="2025-04-27T12:00:00Z",
    )
    assert photo.id == "uuid-1234"
    assert photo.metadata.description == "desc"
    assert photo.last_modified == "2025-04-27T12:00:00Z"

def test_photo_model_missing_fields():
    meta = schemas.PhotoMetadataFields(description="desc")
    with pytest.raises(ValidationError):
        schemas.Photo(
            object_key="photos/uuid-1234.jpg",
            metadata=meta,
            last_modified="2025-04-27T12:00:00Z",
        )

def test_update_metadata_request_valid():
    req = schemas.UpdateMetadataRequest(metadata={"description": "desc"})
    assert req.metadata["description"] == "desc"

def test_update_metadata_request_missing_metadata():
    with pytest.raises(ValidationError):
        schemas.UpdateMetadataRequest()
