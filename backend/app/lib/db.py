from __future__ import annotations

import logging

import psycopg
from pgvector.psycopg import register_vector
from psycopg_pool import ConnectionPool

from app.lib.config import config

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None


def _get_database_url(database_url: str | None = None) -> str:
    url = database_url or config.DATABASE_URL
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Configure it in your environment or .env file."
        )
    return url


def _configure_connection(conn: psycopg.Connection) -> None:
    """Called for every new connection in the pool: registers the pgvector type codec."""
    register_vector(conn)


def init_pool(database_url: str | None = None) -> None:
    """Open the connection pool. Call once at application startup."""
    global _pool
    url = _get_database_url(database_url)
    _pool = ConnectionPool(
        conninfo=url,
        min_size=2,
        max_size=5,
        open=False,
        configure=_configure_connection,
    )
    _pool.open(wait=True)
    logger.info("Connected to PostgreSQL")


def close_pool() -> None:
    """Close the connection pool. Call once at application shutdown."""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def get_pool() -> ConnectionPool:
    """Return the active connection pool. Raises RuntimeError if not initialized."""
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_pool() first.")
    return _pool


def initialize_schema() -> None:
    """
    Create all tables, indexes, and the pgvector extension on first startup.
    All statements are idempotent (IF NOT EXISTS). Raises RuntimeError if pgvector
    is not installed on the PostgreSQL instance.
    """
    dim = config.EMBEDDING_DIMENSION
    with psycopg.connect(_get_database_url()) as conn:
        # Enable pgvector extension — fail fast with a clear message if not available.
        try:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        except Exception as exc:
            raise RuntimeError(
                "pgvector extension is not installed on the PostgreSQL instance. "
                "Use the 'pgvector/pgvector:pg16' Docker image or install pgvector manually."
            ) from exc

        logger.info("pgvector extension verified")

        # Sessions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          TEXT PRIMARY KEY,
                name        TEXT,
                external_link TEXT,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)

        # Reports
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id          TEXT PRIMARY KEY,
                session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                content     TEXT NOT NULL,
                question    TEXT,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS reports_session_id_idx ON reports(session_id);
        """)

        # Session log extent (one row per session, nanosecond timestamps)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session_log_extent (
                session_id  TEXT PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,
                start_ns    BIGINT NOT NULL,
                end_ns      BIGINT NOT NULL
            );
        """)

        # Session upload summary (one row per session — last upload wins)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session_upload_summary (
                session_id          TEXT PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,
                uploaded_file_name  TEXT,
                status              TEXT NOT NULL DEFAULT 'pending',
                files_processed     INTEGER NOT NULL DEFAULT 0,
                files_skipped       INTEGER NOT NULL DEFAULT 0,
                lines_parsed        INTEGER NOT NULL DEFAULT 0,
                lines_rejected      INTEGER NOT NULL DEFAULT 0,
                error               TEXT,
                updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)

        # Knowledge chunks
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id              BIGSERIAL PRIMARY KEY,
                content         TEXT NOT NULL,
                source_path     TEXT,
                document_type   TEXT,
                metadata        JSONB,
                embedding       vector({dim})
            );
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS knowledge_chunks_hnsw_idx
                ON knowledge_chunks
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
        """)

        conn.commit()

    logger.info("Schema initialized")
