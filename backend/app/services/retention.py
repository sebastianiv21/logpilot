"""Automatic session retention cleanup."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from app.lib.config import config
from app.lib.loki_client import delete_logs
from app.lib.repositories import SessionRepository

logger = logging.getLogger(__name__)


def _parse_session_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _session_has_any_logs(repo: SessionRepository, session_id: str) -> bool:
    if repo.get_log_extent(session_id) is not None:
        return True
    summary = repo.get_upload_summary(session_id)
    return summary is not None and summary["status"] in {"success", "partial"}


def collect_sessions_for_retention(
    sessions: list,
    *,
    max_count: int,
    max_age_days: int,
    now: datetime | None = None,
) -> list[str]:
    """Return session ids to delete, oldest first, based on age and count rules."""
    current = now or datetime.now(UTC)
    by_age: set[str] = set()
    if max_age_days > 0:
        cutoff = current - timedelta(days=max_age_days)
        by_age = {
            session.id
            for session in sessions
            if _parse_session_time(session.created_at) < cutoff
        }

    by_count: set[str] = set()
    if max_count > 0 and len(sessions) > max_count:
        by_count = {session.id for session in sessions[max_count:]}

    selected_ids = by_age | by_count
    oldest_first = sorted(sessions, key=lambda session: _parse_session_time(session.created_at))
    return [session.id for session in oldest_first if session.id in selected_ids]


def run_session_retention_cleanup() -> list[str]:
    """Delete unpinned sessions according to retention settings. Returns deleted session ids."""
    if not config.SESSION_RETENTION_ENABLED:
        return []

    repo = SessionRepository()
    sessions = repo.list_unpinned()
    session_ids = collect_sessions_for_retention(
        sessions,
        max_count=config.SESSION_RETENTION_MAX_COUNT,
        max_age_days=config.SESSION_RETENTION_MAX_AGE_DAYS,
    )
    deleted_ids: list[str] = []

    for session_id in session_ids:
        try:
            if _session_has_any_logs(repo, session_id):
                extent = repo.get_log_extent(session_id)
                if extent is None:
                    delete_logs(session_id=session_id, start_ns=0, end_ns=None)
                else:
                    delete_logs(session_id=session_id, start_ns=extent[0], end_ns=extent[1])
            if repo.delete(session_id):
                deleted_ids.append(session_id)
        except Exception:
            logger.exception("Failed to clean up retained session %s", session_id)

    if deleted_ids:
        logger.info("Session retention deleted %d session(s)", len(deleted_ids))
    return deleted_ids
