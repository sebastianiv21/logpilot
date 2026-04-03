from __future__ import annotations

import json
import logging
from typing import Any

import numpy as np

from app.lib.db import get_pool

logger = logging.getLogger(__name__)

# Insert in batches to keep memory and transaction size reasonable.
UPSERT_BATCH_SIZE = 500


def upsert_chunks(
    chunks: list[dict[str, Any]],
    *,
    content_key: str = "content",
    embedding_key: str = "embedding",
    source_path_key: str = "source_path",
    document_type_key: str = "document_type",
    metadata_key: str = "metadata",
) -> None:
    """
    Insert chunk records into knowledge_chunks in batches. Each chunk must have
    content and embedding; source_path, document_type, metadata are optional.
    """
    if not chunks:
        return

    rows = []
    for ch in chunks:
        embedding = ch.get(embedding_key)
        if embedding is None:
            continue
        rows.append((
            ch.get(content_key, ""),
            ch.get(source_path_key) or None,
            ch.get(document_type_key) or None,
            json.dumps(ch.get(metadata_key) or {}),
            np.array(embedding, dtype=np.float32),
        ))

    with get_pool().connection() as conn:
        for i in range(0, len(rows), UPSERT_BATCH_SIZE):
            batch = rows[i : i + UPSERT_BATCH_SIZE]
            conn.executemany(
                "INSERT INTO knowledge_chunks "
                "(content, source_path, document_type, metadata, embedding) "
                "VALUES (%s, %s, %s, %s::jsonb, %s)",
                batch,
            )
        conn.commit()

    logger.debug("Upserted %d knowledge chunks", len(rows))


def search(
    query_embedding: list[float],
    limit: int = 10,
    *,
    document_type_filter: str | list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Semantic search over knowledge_chunks using cosine similarity (HNSW index).
    Returns chunks with content, source_path, document_type, metadata, score.
    If document_type_filter is a list, returns chunks matching any of the types.
    """
    query_vec = np.array(query_embedding, dtype=np.float32)

    with get_pool().connection() as conn:
        conn.execute("SET hnsw.ef_search = 40")

        if document_type_filter is None:
            rows = conn.execute(
                "SELECT content, source_path, document_type, metadata, "
                "1 - (embedding <=> %s) AS score "
                "FROM knowledge_chunks "
                "ORDER BY embedding <=> %s "
                "LIMIT %s",
                (query_vec, query_vec, limit),
            ).fetchall()
        elif isinstance(document_type_filter, str):
            rows = conn.execute(
                "SELECT content, source_path, document_type, metadata, "
                "1 - (embedding <=> %s) AS score "
                "FROM knowledge_chunks "
                "WHERE document_type = %s "
                "ORDER BY embedding <=> %s "
                "LIMIT %s",
                (query_vec, document_type_filter, query_vec, limit),
            ).fetchall()
        else:
            # list[str] — match any type in the list
            rows = conn.execute(
                "SELECT content, source_path, document_type, metadata, "
                "1 - (embedding <=> %s) AS score "
                "FROM knowledge_chunks "
                "WHERE document_type = ANY(%s) "
                "ORDER BY embedding <=> %s "
                "LIMIT %s",
                (query_vec, list(document_type_filter), query_vec, limit),
            ).fetchall()

    return [
        {
            "content": row[0],
            "source_path": row[1] or "",
            "document_type": row[2] or "",
            "metadata": row[3] or {},
            "score": float(row[4]),
        }
        for row in rows
    ]


def delete_all() -> None:
    """Delete all knowledge chunks (e.g. before a full re-ingest)."""
    with get_pool().connection() as conn:
        conn.execute("DELETE FROM knowledge_chunks")
        conn.commit()
    logger.debug("Deleted all knowledge chunks")
