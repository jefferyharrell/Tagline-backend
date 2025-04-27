"""
Authentication utilities for E2E tests using cookie-based authentication.
"""

import os

import requests


def login() -> requests.Session:
    """
    Authenticate with the backend and return a session with authentication cookies set.

    Returns:
        requests.Session: A session with auth cookies
    """
    # Get the backend URL from environment variables
    backend_url = os.getenv(
        "TAGLINE_BACKEND_URL", os.getenv("E2E_API_URL", "http://localhost:8000")
    )

    # Get password from environment
    password = os.getenv("BACKEND_PASSWORD")
    assert password, "BACKEND_PASSWORD not found in environment or .env file"

    # Create a session that will maintain cookies
    session = requests.Session()

    # Login
    try:
        resp = session.post(
            f"{backend_url}/login", json={"password": password}, timeout=5
        )
        # === START ADDED DEBUGGING ===
        print(f"\n--- Debugging Login Response ({backend_url}/login) ---")
        print(f"Status Code: {resp.status_code}")
        print("Response Headers:")
        for key, value in resp.headers.items():
            print(f"  {key}: {value}")
        print("Session Cookies BEFORE raise_for_status:")
        print(session.cookies)
        print("Response Body Text:")
        print(resp.text)
        print("------------------------------------------\n")
        # === END ADDED DEBUGGING ===
        resp.raise_for_status()  # Raise exception for 4xx/5xx errors
    except requests.exceptions.RequestException as e:
        # Log details if login fails
        print(f"Login failed: {e}")
        raise

    # Verify login was successful
    assert resp.status_code == 200, f"Login failed: {resp.text}"

    return session


def get_auth_session() -> requests.Session:
    """
    Get an authenticated session with cookies.

    Returns:
        requests.Session: Session with auth cookies
    """
    session = login()
    print("--- Debugging Session Cookies Before Assertion ---")
    print(session.cookies)
    print("----------------------------------------------")
    return session


# This function is no longer needed as we've migrated to cookie-only auth.
# Keeping a stub version that raises an error in case any tests still call it.
def get_access_token() -> str:
    """
    [DEPRECATED] Previously returned an access token for JWT header auth.
    Now that we use cookie-based auth exclusively, this function should not be used.

    Raises:
        DeprecationWarning: This function is deprecated and should not be used.
    """
    raise DeprecationWarning(
        "get_access_token() is deprecated. We use cookie-based auth only. Update your tests."
    )
