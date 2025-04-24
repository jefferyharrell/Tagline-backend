"""
Unit tests for RefreshRequest and RefreshResponse models.
"""

import pytest
from pydantic import ValidationError

from app.schemas import RefreshRequest, RefreshResponse


def test_refresh_request_valid():
    req = RefreshRequest(refresh_token="sometoken")
    assert req.refresh_token == "sometoken"


def test_refresh_request_missing_token():
    with pytest.raises(ValidationError):
        RefreshRequest()  # type: ignore[reportCallIssue]


def test_refresh_request_wrong_type():
    with pytest.raises(ValidationError):
        RefreshRequest(refresh_token=1234)  # type: ignore[reportArgumentType]


def test_refresh_response_valid():
    resp = RefreshResponse(
        access_token="access",
        refresh_token="refresh",
        token_type="bearer",
        expires_in=3600,
        refresh_expires_in=7200,
    )
    assert resp.access_token == "access"
    assert resp.refresh_token == "refresh"
    assert resp.token_type == "bearer"
    assert resp.expires_in == 3600
    assert resp.refresh_expires_in == 7200
