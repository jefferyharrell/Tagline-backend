from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@patch("app.routes.auth.AuthService")
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
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "access"
    assert data["refresh_token"] == "refresh"
    assert data["expires_in"] == 123
    assert data["refresh_expires_in"] == 456
    assert data["token_type"] == "bearer"


@patch("app.routes.auth.AuthService")
def test_login_invalid_password(mock_auth_service, client):
    mock_auth_service.return_value.verify_password.return_value = False
    payload = {"password": "wrong"}
    response = client.post("/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid password"


@patch("app.routes.auth.AuthService")
def test_refresh_success(mock_auth_service, client):
    mock_auth_service.return_value.refresh_tokens.return_value = (
        "access",
        "refresh",
        123,
        456,
    )
    payload = {"refresh_token": "goodtoken"}
    response = client.post("/refresh", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "access"
    assert data["refresh_token"] == "refresh"
    assert data["expires_in"] == 123
    assert data["refresh_expires_in"] == 456
    assert data["token_type"] == "bearer"


@patch("app.routes.auth.AuthService")
def test_refresh_invalid_token(mock_auth_service, client):
    mock_auth_service.return_value.refresh_tokens.side_effect = Exception("fail")
    payload = {"refresh_token": "badtoken"}
    response = client.post("/refresh", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired refresh token"
