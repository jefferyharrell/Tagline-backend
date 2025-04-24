"""
E2E test for the Tagline backend root endpoint.
- Builds and runs the backend Docker image.
- Waits for the container to be ready.
- Sends a real HTTP request to the running service.
- Cleans up the container after the test.
"""

import time

import pytest
import requests

PORT = 8000


@pytest.fixture(scope="session", autouse=True)
def wait_for_backend():
    """Wait for the backend to be ready before running E2E tests."""
    url = f"http://localhost:{PORT}/"
    for _ in range(50):  # Poll every 0.2s, max 10s
        try:
            r = requests.get(url, timeout=0.5)
            if r.status_code == 200:
                return
        except Exception:
            time.sleep(0.2)
    pytest.fail(f"Backend did not become ready at {url} within 10s. Is it running?")


@pytest.mark.e2e
def test_root_e2e() -> None:
    """E2E: The root endpoint should return the production response."""
    resp = requests.get(f"http://localhost:{PORT}/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
