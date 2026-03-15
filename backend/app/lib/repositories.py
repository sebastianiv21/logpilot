"""Session and Report repositories (CRUD and list/get)."""

import sqlite3
import uuid
from datetime import UTC, datetime

from app.lib.config import config
from app.lib.db import get_connection, init_schema
from app.models.report import Report
from app.models.session import Session


def _iso_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _row_to_session(row: sqlite3.Row) -> Session:
    return Session(
        id=row["id"],
        name=row["name"],
        external_link=row["external_link"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_report(row: sqlite3.Row) -> Report:
    return Report(
        id=row["id"],
        session_id=row["session_id"],
        content=row["content"],
        created_at=row["created_at"],
    )


class SessionRepository:
    """CRUD for sessions."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._conn = conn
        self._own_conn = conn is None

    def _connection(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        conn = get_connection(config.db_path)
        init_schema(conn)
        return conn

    def create(self, name: str | None = None, external_link: str | None = None) -> Session:
        now = _iso_now()
        sid = str(uuid.uuid4())
        conn = self._connection()
        try:
            conn.execute(
                "INSERT INTO sessions (id, name, external_link, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (sid, name, external_link, now, now),
            )
            conn.commit()
        finally:
            if self._own_conn and self._conn is None:
                conn.close()
        return Session(
            id=sid, name=name, external_link=external_link, created_at=now, updated_at=now
        )

    def get(self, session_id: str) -> Session | None:
        conn = self._connection()
        try:
            row = conn.execute(
                "SELECT id, name, external_link, created_at, updated_at FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            if row is None:
                return None
            return _row_to_session(row)
        finally:
            if self._own_conn and self._conn is None:
                conn.close()

    def list_all(self) -> list[Session]:
        conn = self._connection()
        try:
            rows = conn.execute(
                "SELECT id, name, external_link, created_at, updated_at FROM sessions "
                "ORDER BY created_at DESC"
            ).fetchall()
            return [_row_to_session(r) for r in rows]
        finally:
            if self._own_conn and self._conn is None:
                conn.close()

    def update(
        self,
        session_id: str,
        name: str | None = None,
        external_link: str | None = None,
    ) -> Session | None:
        existing = self.get(session_id)
        if existing is None:
            return None
        updates: list[str] = []
        params: list[object] = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if external_link is not None:
            updates.append("external_link = ?")
            params.append(external_link)
        if not updates:
            return existing
        now = _iso_now()
        updates.append("updated_at = ?")
        params.append(now)
        params.append(session_id)
        conn = self._connection()
        try:
            conn.execute(f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
        finally:
            if self._own_conn and self._conn is None:
                conn.close()
        return Session(
            id=existing.id,
            name=name if name is not None else existing.name,
            external_link=external_link if external_link is not None else existing.external_link,
            created_at=existing.created_at,
            updated_at=now,
        )

    def get_log_extent(self, session_id: str) -> tuple[int, int] | None:
        """Return (start_ns, end_ns) for the session's logged time range, or None if never updated."""
        conn = self._connection()
        try:
            row = conn.execute(
                "SELECT start_ns, end_ns FROM session_log_extent WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row is None:
                return None
            return (int(row["start_ns"]), int(row["end_ns"]))
        finally:
            if self._own_conn and self._conn is None:
                conn.close()

    def update_log_extent(
        self, session_id: str, batch_start_ns: int, batch_end_ns: int
    ) -> None:
        """Extend the session's log time range with this batch (min/max with existing if any)."""
        conn = self._connection()
        try:
            existing = conn.execute(
                "SELECT start_ns, end_ns FROM session_log_extent WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if existing is None:
                conn.execute(
                    "INSERT INTO session_log_extent (session_id, start_ns, end_ns) VALUES (?, ?, ?)",
                    (session_id, batch_start_ns, batch_end_ns),
                )
            else:
                start_ns = min(int(existing["start_ns"]), batch_start_ns)
                end_ns = max(int(existing["end_ns"]), batch_end_ns)
                conn.execute(
                    "UPDATE session_log_extent SET start_ns = ?, end_ns = ? WHERE session_id = ?",
                    (start_ns, end_ns, session_id),
                )
            conn.commit()
        finally:
            if self._own_conn and self._conn is None:
                conn.close()

    def get_upload_summary(
        self, session_id: str
    ) -> dict[str, str | int | None] | None:
        """Return the last upload summary for the session, or None if never uploaded."""
        conn = self._connection()
        try:
            row = conn.execute(
                "SELECT session_id, status, files_processed, files_skipped, "
                "lines_parsed, lines_rejected, error, updated_at, uploaded_file_name "
                "FROM session_upload_summary WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row is None:
                return None
            return {
                "session_id": row["session_id"],
                "status": row["status"],
                "files_processed": int(row["files_processed"]),
                "files_skipped": int(row["files_skipped"]),
                "lines_parsed": int(row["lines_parsed"]),
                "lines_rejected": int(row["lines_rejected"]),
                "error": row["error"],
                "updated_at": row["updated_at"],
                "uploaded_file_name": row["uploaded_file_name"],
            }
        finally:
            if self._own_conn and self._conn is None:
                conn.close()

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
        """Insert or replace the last upload summary for the session."""
        now = _iso_now()
        conn = self._connection()
        try:
            conn.execute(
                "INSERT INTO session_upload_summary "
                "(session_id, status, files_processed, files_skipped, lines_parsed, lines_rejected, error, updated_at, uploaded_file_name) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(session_id) DO UPDATE SET "
                "status=excluded.status, files_processed=excluded.files_processed, "
                "files_skipped=excluded.files_skipped, lines_parsed=excluded.lines_parsed, "
                "lines_rejected=excluded.lines_rejected, error=excluded.error, updated_at=excluded.updated_at, "
                "uploaded_file_name=excluded.uploaded_file_name",
                (session_id, status, files_processed, files_skipped, lines_parsed, lines_rejected, error, now, uploaded_file_name),
            )
            conn.commit()
        finally:
            if self._own_conn and self._conn is None:
                conn.close()


class ReportRepository:
    """Create, list by session, get by id for reports."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self._conn = conn
        self._own_conn = conn is None

    def _connection(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        conn = get_connection(config.db_path)
        init_schema(conn)
        return conn

    def create(self, session_id: str, content: str) -> Report:
        rid = str(uuid.uuid4())
        now = _iso_now()
        conn = self._connection()
        try:
            conn.execute(
                "INSERT INTO reports (id, session_id, content, created_at) VALUES (?, ?, ?, ?)",
                (rid, session_id, content, now),
            )
            conn.commit()
        finally:
            if self._own_conn and self._conn is None:
                conn.close()
        return Report(id=rid, session_id=session_id, content=content, created_at=now)

    def list_by_session(self, session_id: str) -> list[Report]:
        conn = self._connection()
        try:
            rows = conn.execute(
                "SELECT id, session_id, content, created_at FROM reports "
                "WHERE session_id = ? ORDER BY created_at DESC",
                (session_id,),
            ).fetchall()
            return [_row_to_report(r) for r in rows]
        finally:
            if self._own_conn and self._conn is None:
                conn.close()

    def get_by_id(self, report_id: str, session_id: str | None = None) -> Report | None:
        conn = self._connection()
        try:
            if session_id is not None:
                row = conn.execute(
                    "SELECT id, session_id, content, created_at FROM reports "
                    "WHERE id = ? AND session_id = ?",
                    (report_id, session_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT id, session_id, content, created_at FROM reports WHERE id = ?",
                    (report_id,),
                ).fetchone()
            if row is None:
                return None
            return _row_to_report(row)
        finally:
            if self._own_conn and self._conn is None:
                conn.close()

    def update_content(self, report_id: str, session_id: str, content: str) -> bool:
        """Update report content by id and session_id. Returns True if a row was updated."""
        conn = self._connection()
        try:
            cur = conn.execute(
                "UPDATE reports SET content = ? WHERE id = ? AND session_id = ?",
                (content, report_id, session_id),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            if self._own_conn and self._conn is None:
                conn.close()
