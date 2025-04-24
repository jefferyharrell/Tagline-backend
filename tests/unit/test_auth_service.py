"""
Unit tests for AuthService (authentication service logic).
Covers password verification, token issuance, validation, and revocation.
"""

from datetime import UTC, datetime, timedelta

import pytest

from app.auth_service import AuthService
from app.models import RefreshToken


@pytest.fixture
def settings(set_filesystem_storage_path):
    from app.config import get_settings

    return get_settings()


@pytest.fixture
def auth_service(settings, db_session):
    return AuthService(settings, db_session)


def test_verify_password_correct(auth_service):
    assert auth_service.verify_password("test_password")


def test_verify_password_incorrect(auth_service):
    assert not auth_service.verify_password("wrong_password")


def test_issue_tokens_and_store_refresh(auth_service, db_session):
    access, refresh, access_exp, refresh_exp = auth_service.issue_tokens()
    db_session.flush()
    assert isinstance(access, str)
    assert isinstance(refresh, str)
    # Check refresh token is stored (hashed)
    import hashlib

    token_hash = hashlib.sha256(refresh.encode()).hexdigest()
    db_token = db_session.query(RefreshToken).filter_by(token=token_hash).first()
    assert db_token is not None
    assert not db_token.revoked


def test_validate_access_token(auth_service):
    access, refresh, _, _ = auth_service.issue_tokens()
    payload = auth_service.validate_token(access, token_type="access")
    assert payload is not None
    assert payload["type"] == "access"


def test_refresh_token_db_sanity(auth_service, db_session):
    """Sanity check: Issue a refresh token and confirm it's in the DB."""
    _, refresh, _, _ = auth_service.issue_tokens()
    db_session.flush()
    import hashlib

    token_hash = hashlib.sha256(refresh.encode()).hexdigest()
    db_token = db_session.query(RefreshToken).filter_by(token=token_hash).first()
    assert db_token is not None, f"Refresh token hash {token_hash} not found in DB!"
    assert not db_token.revoked


def test_validate_refresh_token(auth_service, db_session, settings):
    access, refresh, _, _ = auth_service.issue_tokens()
    db_session.flush()
    db_session.expire_all()
    payload = auth_service.validate_token(refresh, token_type="refresh")
    assert payload is not None, "Service validate_token returned None"
    assert payload.get("type") == "refresh"


def test_validate_token_wrong_type(auth_service):
    access, refresh, _, _ = auth_service.issue_tokens()
    # Try to validate access token as refresh
    assert auth_service.validate_token(access, token_type="refresh") is None
    # Try to validate refresh token as access
    assert auth_service.validate_token(refresh, token_type="access") is None


def test_validate_token_expired(auth_service, settings, db_session):
    # Manually craft an expired access token
    from jose import jwt

    expired_exp = int((datetime.now(UTC) - timedelta(seconds=10)).timestamp())
    token = jwt.encode(
        {"exp": expired_exp, "type": "access"},
        str(settings.JWT_SECRET_KEY),
        algorithm="HS256",
    )
    db_session.flush()
    assert auth_service.validate_token(token, token_type="access") is None


def test_revoke_refresh_token(auth_service, db_session):
    _, refresh, _, _ = auth_service.issue_tokens()
    db_session.flush()
    db_session.expire_all()
    # Should be valid before revocation
    assert auth_service.validate_token(refresh, token_type="refresh") is not None
    assert auth_service.revoke_refresh_token(refresh) is True
    # Should be invalid after revocation
    assert auth_service.validate_token(refresh, token_type="refresh") is None
    # Double revocation should fail
    assert auth_service.revoke_refresh_token(refresh) is False


def test_validate_token_revoked(auth_service, db_session):
    _, refresh, _, _ = auth_service.issue_tokens()
    db_session.flush()
    db_session.expire_all()
    assert auth_service.validate_token(refresh, token_type="refresh") is not None
    assert auth_service.revoke_refresh_token(refresh)
    assert auth_service.validate_token(refresh, token_type="refresh") is None
