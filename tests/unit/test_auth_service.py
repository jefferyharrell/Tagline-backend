"""
Unit tests for AuthService (authentication service logic).
Covers password verification, token issuance, validation, and revocation.
"""

from datetime import UTC, datetime, timedelta

import pytest

from tagline_backend_app.auth_service import AuthService
from tests.unit.test_token_store import DummyTokenStore


@pytest.fixture
def settings(set_filesystem_storage_path):
    from tagline_backend_app.config import get_settings

    return get_settings()


@pytest.fixture
def auth_service(settings):
    # Use a dummy in-memory token store for AuthService tests
    return AuthService(settings, DummyTokenStore())


def test_verify_password_correct(auth_service):
    assert auth_service.verify_password("test_password")


def test_verify_password_incorrect(auth_service):
    assert not auth_service.verify_password("wrong_password")


def test_issue_tokens_and_store_refresh(auth_service):
    access, refresh, access_exp, refresh_exp = auth_service.issue_tokens()
    assert isinstance(access, str)
    assert isinstance(refresh, str)
    # Check refresh token is stored in the dummy store
    assert auth_service.token_store.is_refresh_token_valid(refresh)


def test_validate_access_token(auth_service):
    access, refresh, _, _ = auth_service.issue_tokens()
    payload = auth_service.validate_token(access, token_type="access")
    assert payload is not None
    assert payload["type"] == "access"


def test_refresh_token_db_sanity():
    pytest.skip("DB-backed refresh token logic not relevant for DummyTokenStore")


def test_validate_refresh_token(auth_service, settings):
    access, refresh, _, _ = auth_service.issue_tokens()
    # With DummyTokenStore, no DB/session required
    payload = auth_service.validate_token(refresh, token_type="refresh")
    assert payload is not None, "Service validate_token returned None"
    assert payload.get("type") == "refresh"


def test_validate_token_wrong_type(auth_service):
    access, refresh, _, _ = auth_service.issue_tokens()
    # Try to validate access token as refresh
    assert auth_service.validate_token(access, token_type="refresh") is None
    # Try to validate refresh token as access
    assert auth_service.validate_token(refresh, token_type="access") is None


def test_validate_token_expired(auth_service, settings):
    # Manually craft an expired access token
    from jose import jwt

    expired_exp = int((datetime.now(UTC) - timedelta(seconds=10)).timestamp())
    token = jwt.encode(
        {"exp": expired_exp, "type": "access"},
        str(settings.JWT_SECRET_KEY),
        algorithm="HS256",
    )
    # With DummyTokenStore, no DB/session required
    assert auth_service.validate_token(token, token_type="access") is None


def test_revoke_refresh_token(auth_service):
    _, refresh, _, _ = auth_service.issue_tokens()
    # Should be valid before revocation
    assert auth_service.validate_token(refresh, token_type="refresh") is not None
    auth_service.revoke_refresh_token(refresh)
    # Should be invalid after revocation
    assert auth_service.validate_token(refresh, token_type="refresh") is None
    # Double revocation should not raise
    auth_service.revoke_refresh_token(refresh)


def test_validate_token_revoked(auth_service):
    _, refresh, _, _ = auth_service.issue_tokens()
    assert auth_service.validate_token(refresh, token_type="refresh") is not None
    auth_service.revoke_refresh_token(refresh)
    assert auth_service.validate_token(refresh, token_type="refresh") is None
