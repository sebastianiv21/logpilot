"""Unit tests for session retention selection and cleanup behavior."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.models.session import Session
from app.services import retention


def _session(session_id: str, created_at: str, *, is_pinned: bool = False) -> Session:
    return Session(
        id=session_id,
        name=session_id,
        external_link=None,
        is_pinned=is_pinned,
        created_at=created_at,
        updated_at=created_at,
    )


def test_collect_sessions_deletes_oldest_sessions_beyond_count_limit() -> None:
    sessions = [
        _session("newest", "2026-04-03T12:00:00Z"),
        _session("middle", "2026-04-02T12:00:00Z"),
        _session("oldest", "2026-04-01T12:00:00Z"),
    ]

    selected = retention.collect_sessions_for_retention(
        sessions,
        max_count=2,
        max_age_days=0,
        now=datetime(2026, 4, 3, 12, 0, tzinfo=UTC),
    )

    assert selected == ["oldest"]


def test_collect_sessions_deletes_sessions_older_than_age_limit() -> None:
    sessions = [
        _session("fresh", "2026-04-03T12:00:00Z"),
        _session("stale", "2026-02-15T12:00:00Z"),
    ]

    selected = retention.collect_sessions_for_retention(
        sessions,
        max_count=0,
        max_age_days=30,
        now=datetime(2026, 4, 3, 12, 0, tzinfo=UTC),
    )

    assert selected == ["stale"]


def test_collect_sessions_unions_age_and_count_rules_oldest_first() -> None:
    sessions = [
        _session("fresh", "2026-04-03T12:00:00Z"),
        _session("count-only", "2026-04-02T12:00:00Z"),
        _session("age-and-count", "2026-03-01T12:00:00Z"),
    ]

    selected = retention.collect_sessions_for_retention(
        sessions,
        max_count=1,
        max_age_days=30,
        now=datetime(2026, 4, 3, 12, 0, tzinfo=UTC),
    )

    assert selected == ["age-and-count", "count-only"]


def test_cleanup_skips_when_retention_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(retention.config, "SESSION_RETENTION_ENABLED", False)

    assert retention.run_session_retention_cleanup() == []


def test_cleanup_deletes_only_targeted_sessions(monkeypatch: pytest.MonkeyPatch) -> None:
    deleted_from_loki: list[str] = []
    deleted_from_repo: list[str] = []

    class FakeRepo:
        def list_unpinned(self) -> list[Session]:
            return [
                _session("keep", "2026-04-03T12:00:00Z"),
                _session("delete-me", "2026-03-01T12:00:00Z"),
            ]

        def get_log_extent(self, session_id: str):
            return (10, 20) if session_id == "delete-me" else None

        def get_upload_summary(self, session_id: str):
            return {"status": "success"} if session_id == "delete-me" else None

        def delete(self, session_id: str) -> bool:
            deleted_from_repo.append(session_id)
            return True

    monkeypatch.setattr(retention, "SessionRepository", lambda: FakeRepo())
    monkeypatch.setattr(
        retention,
        "delete_logs",
        lambda **kwargs: deleted_from_loki.append(kwargs["session_id"]),
    )
    monkeypatch.setattr(retention.config, "SESSION_RETENTION_ENABLED", True)
    monkeypatch.setattr(retention.config, "SESSION_RETENTION_MAX_COUNT", 20)
    monkeypatch.setattr(retention.config, "SESSION_RETENTION_MAX_AGE_DAYS", 30)

    deleted = retention.run_session_retention_cleanup()

    assert deleted == ["delete-me"]
    assert deleted_from_loki == ["delete-me"]
    assert deleted_from_repo == ["delete-me"]


def test_cleanup_does_not_delete_repo_row_when_loki_delete_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeRepo:
        def list_unpinned(self) -> list[Session]:
            return [_session("session-1", "2026-03-01T12:00:00Z")]

        def get_log_extent(self, session_id: str):
            return (10, 20)

        def get_upload_summary(self, session_id: str):
            return {"status": "success"}

        def delete(self, session_id: str) -> bool:
            raise AssertionError("delete should not be called when Loki deletion fails")

    monkeypatch.setattr(retention, "SessionRepository", lambda: FakeRepo())
    monkeypatch.setattr(
        retention,
        "delete_logs",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("loki unavailable")),
    )
    monkeypatch.setattr(retention.config, "SESSION_RETENTION_ENABLED", True)
    monkeypatch.setattr(retention.config, "SESSION_RETENTION_MAX_COUNT", 20)
    monkeypatch.setattr(retention.config, "SESSION_RETENTION_MAX_AGE_DAYS", 30)

    assert retention.run_session_retention_cleanup() == []
