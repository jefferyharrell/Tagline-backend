"""
E2E tests for the /refresh endpoint.
"""

import pytest
import requests

API_URL = "http://localhost:8000"


@pytest.mark.e2e
def test_refresh_valid_login_and_refresh():
    # Step 1: Login to get refresh token
    login_resp = requests.post(f"{API_URL}/login", json={"password": "abc123"})
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]

    # Step 2: Use refresh token to get new tokens
    refresh_resp = requests.post(
        f"{API_URL}/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]


@pytest.mark.e2e
def test_refresh_revoked_token_cannot_be_used():
    """
    E2E: After a refresh token is used, it is revoked and cannot be used again.
    """
    # Step 1: Login to get refresh token
    login_resp = requests.post(f"{API_URL}/login", json={"password": "abc123"})
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]

    # Step 2: Use refresh token to get new tokens (revokes the original refresh token)
    refresh_resp = requests.post(
        f"{API_URL}/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200

    # Step 3: Attempt to use the revoked refresh token again
    second_resp = requests.post(
        f"{API_URL}/refresh", json={"refresh_token": refresh_token}
    )
    assert second_resp.status_code == 401
    assert "Invalid or expired refresh token" in second_resp.text


@pytest.mark.e2e
@pytest.mark.parametrize(
    "bad_payload,expected_status",
    [
        ({}, 422),  # Missing refresh_token
        ({"refresh_token": 123}, 422),  # Wrong type
        ({"refresh_token": "notavalidtoken"}, 401),  # Invalid/unknown token
    ],
)
def test_refresh_invalid_payloads(bad_payload, expected_status):
    resp = requests.post(f"{API_URL}/refresh", json=bad_payload)
    assert resp.status_code == expected_status
