"""Qdrant client: store and search knowledge chunks with embeddings."""

from __future__ import annotations

import uuid
from typing import Any

from qdrant_client import QdrantClient as QdrantClientLib
from qdrant_client.http import models as qmodels

from app.lib.config import config

COLLECTION_NAME = "logpilot_knowledge"


def _client() -> QdrantClientLib:
    return QdrantClientLib(url=config.QDRANT_URL)


def ensure_collection(*, dimension: int = 0) -> None:
    """Create the knowledge collection if it does not exist. dimension from config if 0."""
    dim = dimension or config.EMBEDDING_DIMENSION
    client = _client()
    collections = client.get_collections().collections
    if any(c.name == COLLECTION_NAME for c in collections):
        return
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=qmodels.VectorParams(size=dim, distance=qmodels.Distance.COSINE),
    )


# Qdrant HTTP API has a ~32 MB payload limit per request; batch upserts to stay under it.
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
    Upsert chunk records into Qdrant in batches. Each chunk must have content, embedding,
    and optional source_path, document_type, metadata. Ids are generated if not present.
    """
    if not chunks:
        return
    points = []
    for ch in chunks:
        embedding = ch.get(embedding_key)
        if embedding is None:
            continue
        point_id = ch.get("id")
        if point_id is None:
            point_id = str(uuid.uuid4())
        payload = {
            content_key: ch.get(content_key, ""),
            source_path_key: ch.get(source_path_key) or "",
            document_type_key: ch.get(document_type_key) or "",
            metadata_key: ch.get(metadata_key) or {},
        }
        points.append(
            qmodels.PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload,
            )
        )
    dim = len(chunks[0].get(embedding_key, []))
    ensure_collection(dimension=dim)
    client = _client()
    for i in range(0, len(points), UPSERT_BATCH_SIZE):
        batch = points[i : i + UPSERT_BATCH_SIZE]
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch,
        )


def search(
    query_embedding: list[float],
    limit: int = 10,
    *,
    content_key: str = "content",
    source_path_key: str = "source_path",
    metadata_key: str = "metadata",
) -> list[dict[str, Any]]:
    """
    Semantic search: return chunks with content, source_path, metadata.
    """
    ensure_collection()
    client = _client()
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
    )
    results = response.points
    return [
        {
            "content": (h.payload or {}).get(content_key, ""),
            "source_path": (h.payload or {}).get(source_path_key, ""),
            "metadata": (h.payload or {}).get(metadata_key, {}),
        }
        for h in results
    ]


def delete_all() -> None:
    """Delete all points in the knowledge collection (e.g. for full re-ingest)."""
    client = _client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    ensure_collection()
