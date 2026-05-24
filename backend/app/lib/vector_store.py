"""VectorStore protocol + factory.

Decouples the knowledge service from any concrete vector backend. Adding a
new store means dropping an implementation class under
``app/lib/vector_stores/`` and teaching ``get_vector_store()`` to return it.

Why a Protocol (structural typing) and not an ABC: implementations don't need
to inherit from anything. A class with the right method signatures is a
VectorStore. Keeps the existing free-function style of ``pgvector.py``
ergonomic and lets new backends stay independent.
"""

from __future__ import annotations

import os
from typing import Any, Protocol, TypedDict


class Chunk(TypedDict, total=False):
    """A knowledge-store chunk record.

    All keys optional except ``content`` (and ``embedding`` at upsert time).
    Search results omit ``embedding`` and populate ``score``.
    """

    content: str
    embedding: list[float]
    source_path: str
    source_key: str
    file_hash: str
    chunk_index: int
    document_type: str
    metadata: dict[str, Any]
    score: float


class VectorSearchFilters(TypedDict, total=False):
    """Filters accepted by VectorStore.search.

    Each "match" filter (``document_type``, ``source_key``) may be a single
    value or a list (matches any). ``exclude_session_id`` excludes chunks
    whose metadata carries that session_id — used by cross-session incident
    memory to keep the current session out of "have we seen this before?"
    results. Implementations may ignore unknown keys but should never
    silently accept misspelled ones — add a key here when introducing a new
    filter dimension.
    """

    document_type: str | list[str]
    source_key: str | list[str]
    exclude_session_id: str


class VectorStore(Protocol):
    """Read/write interface for the knowledge vector store.

    Methods are sync to match the rest of the codebase. Implementations are
    expected to be thread-safe.
    """

    def upsert(self, chunks: list[Chunk]) -> None:
        """Insert (or replace, at the implementation's discretion) the given
        chunks. Chunks must carry ``content`` and ``embedding`` at minimum.
        No-op if ``chunks`` is empty."""
        ...

    def search(
        self,
        query_embedding: list[float],
        *,
        limit: int = 10,
        filters: VectorSearchFilters | None = None,
    ) -> list[Chunk]:
        """Return up to ``limit`` chunks ranked by similarity to
        ``query_embedding``, optionally narrowed by ``filters``. Results carry
        a ``score`` field (higher is more similar, cosine convention)."""
        ...

    def delete(
        self,
        *,
        source_key: str,
        source_path: str | None = None,
    ) -> None:
        """Delete every chunk for ``source_key``, or just one file's chunks
        when ``source_path`` is also given."""
        ...


def get_vector_store() -> VectorStore:
    """Return the configured backend.

    Selection via the ``VECTOR_STORE`` env var. Defaults to ``pgvector``.
    Imports are lazy so optional backends don't pay startup cost (or fail at
    import time when their optional deps are missing).
    """
    backend = (os.environ.get("VECTOR_STORE") or "pgvector").strip().lower()
    if backend == "pgvector":
        from app.lib.vector_stores.pgvector import PgVectorStore

        return PgVectorStore()
    raise ValueError(
        f"Unknown VECTOR_STORE={backend!r}. "
        "Supported: 'pgvector'. (qdrant lands in a follow-up phase.)"
    )
