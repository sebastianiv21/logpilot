"""PostgreSQL + pgvector implementation of VectorStore.

Lifted from the previous module-level ``app.lib.pg_vector_store`` with no
behavior change — same SQL, same HNSW tuning, same batch size. The only
shape change is moving from module-level functions to a class so the type
conforms to the VectorStore Protocol.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import numpy as np

from app.lib.db import get_pool
from app.lib.vector_store import Chunk, VectorSearchFilters

logger = logging.getLogger(__name__)

# Insert in batches to keep memory and transaction size reasonable.
UPSERT_BATCH_SIZE = 500


class PgVectorStore:
    """VectorStore backed by Postgres with the pgvector extension."""

    def upsert(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return

        rows = []
        for ch in chunks:
            embedding = ch.get("embedding")
            if embedding is None:
                continue
            rows.append(
                (
                    ch.get("content", ""),
                    ch.get("source_path") or None,
                    ch.get("source_key") or None,
                    ch.get("file_hash") or None,
                    ch.get("chunk_index"),
                    ch.get("document_type") or None,
                    json.dumps(ch.get("metadata") or {}),
                    np.array(embedding, dtype=np.float32),
                )
            )

        with get_pool().connection() as conn:
            with conn.cursor() as cur:
                for i in range(0, len(rows), UPSERT_BATCH_SIZE):
                    batch = rows[i : i + UPSERT_BATCH_SIZE]
                    cur.executemany(
                        "INSERT INTO knowledge_chunks "
                        "(content, source_path, source_key, file_hash, chunk_index, "
                        "document_type, metadata, embedding) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)",
                        batch,
                    )
            conn.commit()

        logger.debug("Upserted %d knowledge chunks", len(rows))

    def search(
        self,
        query_embedding: list[float],
        *,
        limit: int = 10,
        filters: VectorSearchFilters | None = None,
    ) -> list[Chunk]:
        query_vec = np.array(query_embedding, dtype=np.float32)
        filters = filters or {}

        with get_pool().connection() as conn:
            conn.execute("SET hnsw.ef_search = 40")
            where_parts: list[str] = []
            params: list[Any] = [query_vec]

            source_filter = filters.get("source_key")
            if source_filter is not None:
                if isinstance(source_filter, str):
                    where_parts.append("source_key = %s")
                    params.append(source_filter)
                else:
                    where_parts.append("source_key = ANY(%s)")
                    params.append(list(source_filter))

            document_type_filter = filters.get("document_type")
            if document_type_filter is not None:
                if isinstance(document_type_filter, str):
                    where_parts.append("document_type = %s")
                    params.append(document_type_filter)
                else:
                    where_parts.append("document_type = ANY(%s)")
                    params.append(list(document_type_filter))

            where_clause = (
                f"WHERE {' AND '.join(where_parts)} " if where_parts else ""
            )
            query = (
                "SELECT content, source_path, source_key, document_type, metadata, "
                "1 - (embedding <=> %s) AS score "
                "FROM knowledge_chunks "
                f"{where_clause}"
                "ORDER BY embedding <=> %s "
                "LIMIT %s"
            )
            params.extend([query_vec, limit])
            rows = conn.execute(query, tuple(params)).fetchall()

        return [
            Chunk(
                content=row[0],
                source_path=row[1] or "",
                source_key=row[2] or "",
                document_type=row[3] or "",
                metadata=row[4] or {},
                score=float(row[5]),
            )
            for row in rows
        ]

    def delete(
        self,
        *,
        source_key: str,
        source_path: str | None = None,
    ) -> None:
        with get_pool().connection() as conn:
            if source_path is None:
                conn.execute(
                    "DELETE FROM knowledge_chunks WHERE source_key = %s",
                    (source_key,),
                )
            else:
                conn.execute(
                    "DELETE FROM knowledge_chunks "
                    "WHERE source_key = %s AND source_path = %s",
                    (source_key, source_path),
                )
            conn.commit()
        if source_path is None:
            logger.debug("Deleted all knowledge chunks for %s", source_key)
        else:
            logger.debug(
                "Deleted knowledge chunks for %s:%s", source_key, source_path
            )
