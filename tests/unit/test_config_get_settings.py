"""
Unit tests for tagline_backend_app.config.get_settings
Ensures get_settings returns a cached singleton instance and is consistent.
"""
import pytest
from tagline_backend_app.config import get_settings, Settings

pytestmark = pytest.mark.unit

def test_get_settings_returns_singleton(monkeypatch):
    # Patch Settings.model_config to ignore .env for deterministic test
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
    assert isinstance(s1, Settings)
    assert s1.APP_ENV == "production"


def test_get_settings_cache_clear(monkeypatch):
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
    s1 = get_settings()
    monkeypatch.setenv("APP_ENV", "development")
    # Should still return the original cached instance
    s2 = get_settings()
    assert s1 is s2
    assert s2.APP_ENV == "production"
    # Now clear cache and check new instance
    get_settings.cache_clear()
    s3 = get_settings()
    assert s3 is not s1
    assert s3.APP_ENV == "development"
