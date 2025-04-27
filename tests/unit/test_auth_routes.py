from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tagline_backend_app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@patch("tagline_backend_app.routes.auth.AuthService")
def test_login_success(mock_auth_service, client):
    mock_auth_service.return_value.verify_password.return_value = True
    mock_auth_service.return_value.issue_tokens.return_value = (
        "access",
        "refresh",
        123,
        456,
    )
    payload = {"password": "secret"}
    response = client.post("/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    # Check if cookies are set correctly
    assert "tagline_access_token" in response.cookies
    assert "tagline_refresh_token" in response.cookies
    assert response.cookies["tagline_access_token"] == "access"
    assert response.cookies["tagline_refresh_token"] == "refresh"
    # Ensure response body is correct
    assert response.json() == {"detail": "Login successful"}


@patch("tagline_backend_app.routes.auth.AuthService")
def test_login_invalid_password(mock_auth_service, client):
    mock_auth_service.return_value.verify_password.return_value = False
    payload = {"password": "wrong"}
    response = client.post("/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid password"


@patch("tagline_backend_app.routes.auth.AuthService")
def test_refresh_success(mock_auth_service, client):
    mock_auth_service.return_value.refresh_tokens.return_value = (
        "access",
        "refresh",
        123,
        456,
    )
    payload = {"refresh_token": "goodtoken"}
    response = client.post("/refresh", json=payload)
    assert response.status_code == status.HTTP_200_OK
    # Check if cookies are set correctly
    assert "tagline_access_token" in response.cookies
    assert "tagline_refresh_token" in response.cookies
    assert response.cookies["tagline_access_token"] == "access"
    assert response.cookies["tagline_refresh_token"] == "refresh"
    # Ensure response body is correct
    assert response.json() == {"detail": "Token refreshed successfully"}


@patch("tagline_backend_app.routes.auth.AuthService")
def test_refresh_invalid_token(mock_auth_service, client):
    mock_auth_service.return_value.refresh_tokens.side_effect = Exception("fail")
    payload = {"refresh_token": "badtoken"}
    response = client.post("/refresh", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token"
