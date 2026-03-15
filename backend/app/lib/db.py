"""SQLite schema and initialization for sessions and reports (MVP metadata store)."""

import sqlite3
from pathlib import Path

SCHEMA_SESSIONS = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    name TEXT,
    external_link TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

SCHEMA_REPORTS = """
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
"""

SCHEMA_SESSION_LOG_EXTENT = """
CREATE TABLE IF NOT EXISTS session_log_extent (
    session_id TEXT PRIMARY KEY,
    start_ns INTEGER NOT NULL,
    end_ns INTEGER NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
"""

SCHEMA_SESSION_UPLOAD_SUMMARY = """
CREATE TABLE IF NOT EXISTS session_upload_summary (
    session_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    files_processed INTEGER NOT NULL,
    files_skipped INTEGER NOT NULL,
    lines_parsed INTEGER NOT NULL,
    lines_rejected INTEGER NOT NULL,
    error TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
"""


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """Return a connection to the SQLite database; creates file and parent dir if needed."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Create sessions, reports, session_log_extent, and session_upload_summary tables if they do not exist."""
    conn.executescript(
        SCHEMA_SESSIONS
        + SCHEMA_REPORTS
        + SCHEMA_SESSION_LOG_EXTENT
        + SCHEMA_SESSION_UPLOAD_SUMMARY
    )
    conn.commit()


def init_db(db_path: str | Path) -> sqlite3.Connection:
    """Create database file (and parent directory if needed), apply schema, return connection."""
    conn = get_connection(db_path)
    init_schema(conn)
    return conn
