"""
Smoke test for tagline_backend_app.constants
Ensures constants are as expected
"""
import pytest
from tagline_backend_app import constants

pytestmark = pytest.mark.unit

@pytest.fixture
def expected_constants():
    return {
        "APP_NAME": "Tagline",
        "API_VERSION": "0.1.0",
    }

def test_constants_values(expected_constants):
    assert constants.APP_NAME == expected_constants["APP_NAME"]
    assert constants.API_VERSION == expected_constants["API_VERSION"]
