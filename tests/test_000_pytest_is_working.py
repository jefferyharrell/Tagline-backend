"""
This test always passes and exists solely to verify that pytest is working.
It should always be the first test run in the suite.
"""

import pytest


@pytest.mark.order(0)
def test_pytest_is_working():
    """Sanity check: pytest is working."""
    assert True
