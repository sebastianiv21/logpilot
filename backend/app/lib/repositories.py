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
