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


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """Return a connection to the SQLite database; creates file and parent dir if needed."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Create sessions and reports tables if they do not exist."""
    conn.executescript(SCHEMA_SESSIONS + SCHEMA_REPORTS)
    conn.commit()


def init_db(db_path: str | Path) -> sqlite3.Connection:
    """Create database file (and parent directory if needed), apply schema, return connection."""
    conn = get_connection(db_path)
    init_schema(conn)
    return conn
