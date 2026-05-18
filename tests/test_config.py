"""Tests for application settings and validation."""

import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from planogram.config import Settings


class _Settings(Settings):
    """Settings subclass that never reads from .env, for test isolation."""

    model_config = SettingsConfigDict(env_file=None, env_file_encoding="utf-8")


class TestSettings:
    def test_missing_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValidationError, match="ANTHROPIC_API_KEY must be set"):
            _Settings()

    def test_empty_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValidationError, match="ANTHROPIC_API_KEY must be set"):
            _Settings(anthropic_api_key="")

    def test_valid_api_key(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        settings = _Settings()
        assert settings.anthropic_api_key == "sk-ant-test"

    def test_default_calendar_id(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        settings = _Settings()
        assert settings.google_calendar_id == "primary"

    def test_default_timezone(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        settings = _Settings()
        assert settings.timezone == "America/New_York"

    def test_default_maps_key_empty(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        settings = _Settings()
        assert settings.google_maps_api_key == ""

    def test_override_via_env(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        monkeypatch.setenv("GOOGLE_CALENDAR_ID", "custom@group.calendar.google.com")
        settings = _Settings()
        assert settings.google_calendar_id == "custom@group.calendar.google.com"
