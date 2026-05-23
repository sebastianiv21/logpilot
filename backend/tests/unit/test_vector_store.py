"""Unit tests for the VectorStore protocol, factory, and PgVectorStore.

The pgvector implementation needs a Postgres connection at call time, but
its query construction can be exercised with a fake pool — that's enough to
catch regressions in SQL shape, filter handling, and method dispatch.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.lib.vector_store import VectorStore, get_vector_store
from app.lib.vector_stores.pgvector import PgVectorStore


class _FakeConn:
    """Minimal psycopg-like Connection that records every SQL call."""

    def __init__(self, rows: list[tuple] | None = None) -> None:
        self.executed: list[tuple[str, tuple[Any, ...] | None]] = []
        self.committed = 0
        self._rows = rows or []

    # context manager: ``with get_pool().connection() as conn:``
    def __enter__(self) -> _FakeConn:
        return self

    def __exit__(self, *exc: Any) -> None:
        return None

    def execute(self, sql: str, params: tuple[Any, ...] | None = None):
        self.executed.append((sql, params))
        cursor = MagicMock()
        cursor.fetchall.return_value = self._rows
        return cursor

    def cursor(self):
        cur = MagicMock()
        cur.__enter__ = lambda self: self
        cur.__exit__ = lambda *a: None
        return cur

    def commit(self) -> None:
        self.committed += 1


@contextmanager
def _patched_pool(conn: _FakeConn):
    pool = MagicMock()
    pool.connection.return_value = conn
    with patch("app.lib.vector_stores.pgvector.get_pool", return_value=pool):
        yield


class TestProtocolConformance:
    def test_pgvector_is_a_vector_store(self):
        # Structural typing: isinstance() doesn't apply to Protocols by default,
        # but the contract is: a PgVectorStore is assignable to VectorStore.
        store: VectorStore = PgVectorStore()
        assert hasattr(store, "upsert")
        assert hasattr(store, "search")
        assert hasattr(store, "delete")


class TestFactory:
    def test_default_returns_pgvector(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("VECTOR_STORE", raising=False)
        assert isinstance(get_vector_store(), PgVectorStore)

    def test_explicit_pgvector_returns_pgvector(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("VECTOR_STORE", "pgvector")
        assert isinstance(get_vector_store(), PgVectorStore)

    def test_uppercase_and_whitespace_tolerated(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("VECTOR_STORE", "  PGVECTOR  ")
        assert isinstance(get_vector_store(), PgVectorStore)

    def test_unknown_backend_raises(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("VECTOR_STORE", "redis")
        with pytest.raises(ValueError, match="Unknown VECTOR_STORE"):
            get_vector_store()


class TestPgVectorStoreUpsert:
    def test_empty_chunks_is_noop(self):
        conn = _FakeConn()
        with _patched_pool(conn):
            PgVectorStore().upsert([])
        assert conn.executed == []
        assert conn.committed == 0

    def test_chunks_without_embedding_are_skipped(self):
        conn = _FakeConn()
        with _patched_pool(conn):
            PgVectorStore().upsert([{"content": "hi"}])  # no embedding
        # cursor.executemany still runs (with empty rows), but commit happens once.
        assert conn.committed == 1


class TestPgVectorStoreSearch:
    def test_no_filters_omits_where_clause(self):
        conn = _FakeConn(rows=[("hello", "docs/a.md", "docs", "markdown", {}, 0.91)])
        with _patched_pool(conn):
            results = PgVectorStore().search([0.1, 0.2], limit=5)
        # First execute is the SET hnsw.ef_search, second is the search query.
        select_sql = conn.executed[1][0]
        assert "WHERE" not in select_sql
        assert "LIMIT" in select_sql
        assert len(results) == 1
        assert results[0]["content"] == "hello"
        assert results[0]["score"] == pytest.approx(0.91)

    def test_source_key_filter_added_to_where(self):
        conn = _FakeConn(rows=[])
        with _patched_pool(conn):
            PgVectorStore().search(
                [0.0], limit=10, filters={"source_key": "docs"}
            )
        select_sql = conn.executed[1][0]
        assert "source_key = %s" in select_sql

    def test_document_type_list_uses_any(self):
        conn = _FakeConn(rows=[])
        with _patched_pool(conn):
            PgVectorStore().search(
                [0.0],
                limit=10,
                filters={"document_type": ["markdown", "text"]},
            )
        select_sql = conn.executed[1][0]
        assert "document_type = ANY(%s)" in select_sql

    def test_both_filters_combined_with_and(self):
        conn = _FakeConn(rows=[])
        with _patched_pool(conn):
            PgVectorStore().search(
                [0.0],
                limit=10,
                filters={"source_key": "docs", "document_type": "markdown"},
            )
        select_sql = conn.executed[1][0]
        assert "source_key = %s" in select_sql
        assert "document_type = %s" in select_sql
        assert " AND " in select_sql


class TestPgVectorStoreDelete:
    def test_delete_by_source_only(self):
        conn = _FakeConn()
        with _patched_pool(conn):
            PgVectorStore().delete(source_key="docs")
        sql, params = conn.executed[0]
        assert "DELETE FROM knowledge_chunks WHERE source_key = %s" in sql
        assert "source_path" not in sql
        assert params == ("docs",)
        assert conn.committed == 1

    def test_delete_by_source_and_path(self):
        conn = _FakeConn()
        with _patched_pool(conn):
            PgVectorStore().delete(source_key="docs", source_path="docs/a.md")
        sql, params = conn.executed[0]
        assert "source_key = %s AND source_path = %s" in sql
        assert params == ("docs", "docs/a.md")
        assert conn.committed == 1
