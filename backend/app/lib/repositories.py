"""Session and Report repositories (CRUD and list/get) — psycopg3 / PostgreSQL."""

from __future__ import annotations

import uuid
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.lib.config import config
from app.lib.db import get_pool
from app.models.report import Report
from app.models.session import Session


def _iso_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _dt_to_iso(value: Any) -> str:
    """Convert a datetime (from PostgreSQL TIMESTAMPTZ) or str to ISO string."""
    if isinstance(value, datetime):
        return value.isoformat().replace("+00:00", "Z")
    return str(value)


def _normalize_question(question: str | None) -> str | None:
    if question is None:
        return None
    normalized = " ".join(question.split()).strip()
    return normalized or None


def _question_preview(question: str | None, max_length: int = 96) -> str | None:
    normalized = _normalize_question(question)
    if normalized is None:
        return None
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 1].rstrip() + "…"


class SessionRepository:
    """CRUD for sessions — backed by PostgreSQL via psycopg3 connection pool."""

    def create(self, name: str | None = None, external_link: str | None = None) -> Session:
        sid = str(uuid.uuid4())
        with get_pool().connection() as conn:
            row = conn.execute(
                "INSERT INTO sessions (id, name, external_link, is_pinned) VALUES (%s, %s, %s, FALSE) "
                "RETURNING id, name, external_link, is_pinned, created_at, updated_at",
                (sid, name, external_link),
            ).fetchone()
            conn.commit()
        assert row is not None
        return Session(
            id=row[0],
            name=row[1],
            external_link=row[2],
            is_pinned=bool(row[3]),
            created_at=_dt_to_iso(row[4]),
            updated_at=_dt_to_iso(row[5]),
        )

    def get(self, session_id: str) -> Session | None:
        with get_pool().connection() as conn:
            row = conn.execute(
                "SELECT id, name, external_link, is_pinned, created_at, updated_at "
                "FROM sessions WHERE id = %s",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return Session(
            id=row[0],
            name=row[1],
            external_link=row[2],
            is_pinned=bool(row[3]),
            created_at=_dt_to_iso(row[4]),
            updated_at=_dt_to_iso(row[5]),
        )

    def list_all(self) -> list[Session]:
        with get_pool().connection() as conn:
            rows = conn.execute(
                "SELECT id, name, external_link, is_pinned, created_at, updated_at "
                "FROM sessions ORDER BY created_at DESC"
            ).fetchall()
        return [
            Session(
                id=r[0],
                name=r[1],
                external_link=r[2],
                is_pinned=bool(r[3]),
                created_at=_dt_to_iso(r[4]),
                updated_at=_dt_to_iso(r[5]),
            )
            for r in rows
        ]

    def update(
        self,
        session_id: str,
        name: str | None = None,
        external_link: str | None = None,
        is_pinned: bool | None = None,
    ) -> Session | None:
        existing = self.get(session_id)
        if existing is None:
            return None
        updates: list[str] = []
        params: list[object] = []
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if external_link is not None:
            updates.append("external_link = %s")
            params.append(external_link)
        if is_pinned is not None:
            updates.append("is_pinned = %s")
            params.append(is_pinned)
        if not updates:
            return existing
        updates.append("updated_at = NOW()")
        params.append(session_id)
        with get_pool().connection() as conn:
            row = conn.execute(
                f"UPDATE sessions SET {', '.join(updates)} WHERE id = %s "
                "RETURNING id, name, external_link, is_pinned, created_at, updated_at",
                params,
            ).fetchone()
            conn.commit()
        if row is None:
            return None
        return Session(
            id=row[0],
            name=row[1],
            external_link=row[2],
            is_pinned=bool(row[3]),
            created_at=_dt_to_iso(row[4]),
            updated_at=_dt_to_iso(row[5]),
        )

    def list_unpinned(self) -> list[Session]:
        with get_pool().connection() as conn:
            rows = conn.execute(
                "SELECT id, name, external_link, is_pinned, created_at, updated_at "
                "FROM sessions WHERE is_pinned = FALSE ORDER BY created_at DESC"
            ).fetchall()
        return [
            Session(
                id=row[0],
                name=row[1],
                external_link=row[2],
                is_pinned=bool(row[3]),
                created_at=_dt_to_iso(row[4]),
                updated_at=_dt_to_iso(row[5]),
            )
            for row in rows
        ]

    def delete(self, session_id: str) -> bool:
        with get_pool().connection() as conn:
            cur = conn.execute("DELETE FROM sessions WHERE id = %s", (session_id,))
            conn.commit()
            return cur.rowcount > 0

    def get_log_extent(self, session_id: str) -> tuple[int, int] | None:
        """Return (start_ns, end_ns) for the session's logged time range, or None."""
        with get_pool().connection() as conn:
            row = conn.execute(
                "SELECT start_ns, end_ns FROM session_log_extent WHERE session_id = %s",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return (int(row[0]), int(row[1]))

    def update_log_extent(
        self, session_id: str, batch_start_ns: int, batch_end_ns: int
    ) -> None:
        """Extend the session's log time range with this batch (min/max with existing if any)."""
        with get_pool().connection() as conn:
            existing = conn.execute(
                "SELECT start_ns, end_ns FROM session_log_extent WHERE session_id = %s",
                (session_id,),
            ).fetchone()
            if existing is None:
                conn.execute(
                    "INSERT INTO session_log_extent (session_id, start_ns, end_ns) "
                    "VALUES (%s, %s, %s)",
                    (session_id, batch_start_ns, batch_end_ns),
                )
            else:
                start_ns = min(int(existing[0]), batch_start_ns)
                end_ns = max(int(existing[1]), batch_end_ns)
                conn.execute(
                    "UPDATE session_log_extent SET start_ns = %s, end_ns = %s "
                    "WHERE session_id = %s",
                    (start_ns, end_ns, session_id),
                )
            conn.commit()

    def get_upload_summary(self, session_id: str) -> dict[str, Any] | None:
        """Return the last upload summary for the session, or None if never uploaded."""
        with get_pool().connection() as conn:
            row = conn.execute(
                "SELECT session_id, status, files_processed, files_skipped, "
                "lines_parsed, lines_rejected, error, updated_at, uploaded_file_name "
                "FROM session_upload_summary WHERE session_id = %s",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "session_id": row[0],
            "status": row[1],
            "files_processed": int(row[2]),
            "files_skipped": int(row[3]),
            "lines_parsed": int(row[4]),
            "lines_rejected": int(row[5]),
            "error": row[6],
            "updated_at": _dt_to_iso(row[7]),
            "uploaded_file_name": row[8],
        }

    def upsert_upload_summary(
        self,
        session_id: str,
        status: str,
        files_processed: int,
        files_skipped: int,
        lines_parsed: int,
        lines_rejected: int,
        error: str | None = None,
        uploaded_file_name: str | None = None,
    ) -> None:
        """Insert or update the upload summary for the session (one row per session)."""
        with get_pool().connection() as conn:
            conn.execute(
                "INSERT INTO session_upload_summary "
                "(session_id, status, files_processed, files_skipped, lines_parsed, "
                "lines_rejected, error, uploaded_file_name, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW()) "
                "ON CONFLICT (session_id) DO UPDATE SET "
                "status = EXCLUDED.status, "
                "files_processed = EXCLUDED.files_processed, "
                "files_skipped = EXCLUDED.files_skipped, "
                "lines_parsed = EXCLUDED.lines_parsed, "
                "lines_rejected = EXCLUDED.lines_rejected, "
                "error = EXCLUDED.error, "
                "uploaded_file_name = EXCLUDED.uploaded_file_name, "
                "updated_at = EXCLUDED.updated_at",
                (
                    session_id, status, files_processed, files_skipped,
                    lines_parsed, lines_rejected, error, uploaded_file_name,
                ),
            )
            conn.commit()


class ReportRepository:
    """Create, list by session, get by id for reports — backed by PostgreSQL."""

    def create(self, session_id: str, content: str, question: str | None = None) -> Report:
        rid = str(uuid.uuid4())
        normalized_question = _normalize_question(question)
        with get_pool().connection() as conn:
            row = conn.execute(
                "INSERT INTO reports (id, session_id, content, question) "
                "VALUES (%s, %s, %s, %s) "
                "RETURNING id, session_id, content, question, created_at",
                (rid, session_id, content, normalized_question),
            ).fetchone()
            conn.commit()
        assert row is not None
        return Report(
            id=row[0],
            session_id=row[1],
            content=row[2],
            question=row[3],
            created_at=_dt_to_iso(row[4]),
        )

    def list_by_session(self, session_id: str) -> list[Report]:
        with get_pool().connection() as conn:
            rows = conn.execute(
                "SELECT id, session_id, content, question, created_at FROM reports "
                "WHERE session_id = %s ORDER BY created_at DESC",
                (session_id,),
            ).fetchall()
        return [
            Report(
                id=r[0],
                session_id=r[1],
                content=r[2],
                question=r[3],
                created_at=_dt_to_iso(r[4]),
            )
            for r in rows
        ]

    def get_by_id(self, report_id: str, session_id: str | None = None) -> Report | None:
        with get_pool().connection() as conn:
            if session_id is not None:
                row = conn.execute(
                    "SELECT id, session_id, content, question, created_at FROM reports "
                    "WHERE id = %s AND session_id = %s",
                    (report_id, session_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT id, session_id, content, question, created_at FROM reports "
                    "WHERE id = %s",
                    (report_id,),
                ).fetchone()
        if row is None:
            return None
        return Report(
            id=row[0],
            session_id=row[1],
            content=row[2],
            question=row[3],
            created_at=_dt_to_iso(row[4]),
        )

    def update_content(self, report_id: str, session_id: str, content: str) -> bool:
        """Update report content by id and session_id. Returns True if a row was updated."""
        with get_pool().connection() as conn:
            cur = conn.execute(
                "UPDATE reports SET content = %s WHERE id = %s AND session_id = %s",
                (content, report_id, session_id),
            )
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def question_preview(question: str | None, max_length: int = 96) -> str | None:
        """Return a normalized, truncated preview for report history."""
        return _question_preview(question, max_length=max_length)


class KnowledgeRepository:
    """Persistence for knowledge source status and file-level ingest bookkeeping."""

    SOURCE_DEFINITIONS = {
        "code": "Code",
        "docs": "Documentation",
    }

    @staticmethod
    def _configured_paths_for(source_key: str) -> list[str]:
        raw_paths = config.knowledge_sources_by_key.get(source_key, [])
        return [str(Path(p)) for p in raw_paths]

    def sync_configured_paths(self) -> None:
        with get_pool().connection() as conn:
            for source_key, display_name in self.SOURCE_DEFINITIONS.items():
                conn.execute(
                    "INSERT INTO knowledge_sources (source_key, display_name, configured_paths) "
                    "VALUES (%s, %s, %s::jsonb) "
                    "ON CONFLICT (source_key) DO UPDATE SET "
                    "display_name = EXCLUDED.display_name, "
                    "configured_paths = EXCLUDED.configured_paths",
                    (source_key, display_name, json.dumps(self._configured_paths_for(source_key))),
                )
            conn.commit()

    def list_sources(self) -> list[dict[str, Any]]:
        self.sync_configured_paths()
        with get_pool().connection() as conn:
            rows = conn.execute(
                "SELECT source_key, display_name, configured_paths, status, "
                "last_started_at, last_completed_at, last_error, "
                "last_chunks_ingested, last_files_processed, "
                "last_files_skipped_unchanged, last_files_deleted, "
                "last_embedding_model, last_embedding_dimension, last_ingest_mode "
                "FROM knowledge_sources ORDER BY source_key"
            ).fetchall()
        return [
            {
                "source_key": row[0],
                "display_name": row[1],
                "configured_paths": list(row[2] or []),
                "status": row[3],
                "last_started_at": _dt_to_iso(row[4]) if row[4] else None,
                "last_completed_at": _dt_to_iso(row[5]) if row[5] else None,
                "last_error": row[6],
                "last_chunks_ingested": int(row[7] or 0),
                "last_files_processed": int(row[8] or 0),
                "last_files_skipped_unchanged": int(row[9] or 0),
                "last_files_deleted": int(row[10] or 0),
                "last_embedding_model": row[11],
                "last_embedding_dimension": int(row[12]) if row[12] is not None else None,
                "last_ingest_mode": row[13],
            }
            for row in rows
        ]

    def get_source(self, source_key: str) -> dict[str, Any] | None:
        for source in self.list_sources():
            if source["source_key"] == source_key:
                return source
        return None

    def mark_started(self, source_key: str, mode: str) -> None:
        with get_pool().connection() as conn:
            conn.execute(
                "UPDATE knowledge_sources SET status = 'running', last_started_at = NOW(), "
                "last_error = NULL, last_ingest_mode = %s WHERE source_key = %s",
                (mode, source_key),
            )
            conn.commit()

    def mark_completed(self, source_key: str, result: dict[str, Any]) -> None:
        with get_pool().connection() as conn:
            conn.execute(
                "UPDATE knowledge_sources SET status = 'ready', last_completed_at = NOW(), "
                "last_error = NULL, last_chunks_ingested = %s, last_files_processed = %s, "
                "last_files_skipped_unchanged = %s, last_files_deleted = %s, "
                "last_embedding_model = %s, last_embedding_dimension = %s, "
                "last_ingest_mode = %s WHERE source_key = %s",
                (
                    result.get("chunks_ingested", 0),
                    result.get("files_processed", 0),
                    result.get("files_skipped_unchanged", 0),
                    result.get("files_deleted", 0),
                    result.get("embedding_model"),
                    result.get("embedding_dimension"),
                    result.get("mode"),
                    source_key,
                ),
            )
            conn.commit()

    def mark_failed(self, source_key: str, error: str, mode: str) -> None:
        with get_pool().connection() as conn:
            conn.execute(
                "UPDATE knowledge_sources SET status = 'failed', last_completed_at = NOW(), "
                "last_error = %s, last_ingest_mode = %s WHERE source_key = %s",
                (error, mode, source_key),
            )
            conn.commit()

    def list_tracked_files(self, source_key: str) -> dict[str, dict[str, Any]]:
        with get_pool().connection() as conn:
            rows = conn.execute(
                "SELECT source_path, content_hash, chunk_count, last_ingested_at "
                "FROM knowledge_source_files WHERE source_key = %s",
                (source_key,),
            ).fetchall()
        return {
            row[0]: {
                "content_hash": row[1],
                "chunk_count": int(row[2] or 0),
                "last_ingested_at": _dt_to_iso(row[3]) if row[3] else None,
            }
            for row in rows
        }

    def upsert_tracked_file(
        self,
        source_key: str,
        source_path: str,
        content_hash: str,
        chunk_count: int,
    ) -> None:
        with get_pool().connection() as conn:
            conn.execute(
                "INSERT INTO knowledge_source_files "
                "(source_key, source_path, content_hash, chunk_count, last_ingested_at) "
                "VALUES (%s, %s, %s, %s, NOW()) "
                "ON CONFLICT (source_key, source_path) DO UPDATE SET "
                "content_hash = EXCLUDED.content_hash, "
                "chunk_count = EXCLUDED.chunk_count, "
                "last_ingested_at = EXCLUDED.last_ingested_at",
                (source_key, source_path, content_hash, chunk_count),
            )
            conn.commit()

    def delete_tracked_file(self, source_key: str, source_path: str) -> None:
        with get_pool().connection() as conn:
            conn.execute(
                "DELETE FROM knowledge_source_files WHERE source_key = %s AND source_path = %s",
                (source_key, source_path),
            )
            conn.commit()

    def delete_tracked_files_for_source(self, source_key: str) -> None:
        with get_pool().connection() as conn:
            conn.execute(
                "DELETE FROM knowledge_source_files WHERE source_key = %s",
                (source_key,),
            )
            conn.commit()
