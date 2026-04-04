"""Unit tests for env-backed config defaults and overrides."""

from __future__ import annotations

from app.lib.config import Config


def test_retention_config_defaults(monkeypatch) -> None:
    monkeypatch.delenv("SESSION_RETENTION_ENABLED", raising=False)
    monkeypatch.delenv("SESSION_RETENTION_MAX_COUNT", raising=False)
    monkeypatch.delenv("SESSION_RETENTION_MAX_AGE_DAYS", raising=False)

    config = Config()

    assert config.SESSION_RETENTION_ENABLED is True
    assert config.SESSION_RETENTION_MAX_COUNT == 20
    assert config.SESSION_RETENTION_MAX_AGE_DAYS == 30


def test_retention_config_env_overrides(monkeypatch) -> None:
    monkeypatch.setenv("SESSION_RETENTION_ENABLED", "false")
    monkeypatch.setenv("SESSION_RETENTION_MAX_COUNT", "7")
    monkeypatch.setenv("SESSION_RETENTION_MAX_AGE_DAYS", "12")

    config = Config()

    assert config.SESSION_RETENTION_ENABLED is False
    assert config.SESSION_RETENTION_MAX_COUNT == 7
    assert config.SESSION_RETENTION_MAX_AGE_DAYS == 12


def test_retention_config_allows_non_positive_disabling_values(monkeypatch) -> None:
    monkeypatch.setenv("SESSION_RETENTION_MAX_COUNT", "0")
    monkeypatch.setenv("SESSION_RETENTION_MAX_AGE_DAYS", "-1")

    config = Config()

    assert config.SESSION_RETENTION_MAX_COUNT == 0
    assert config.SESSION_RETENTION_MAX_AGE_DAYS == -1
