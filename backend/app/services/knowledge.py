"""Chunking and embedding for persisted code/docs knowledge sources."""

from __future__ import annotations

import logging
import hashlib
from pathlib import Path
from typing import Any

from openai import OpenAI

from app.lib.config import config
from app.lib.pg_vector_store import delete_all, delete_file, upsert_chunks
from app.lib.pg_vector_store import search as pg_search
from app.lib.repositories import KnowledgeRepository

logger = logging.getLogger(__name__)

# Repo file extensions (code and config)
REPO_EXTENSIONS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".cjs",
    ".mjs",
    ".java",
    ".py",
    ".css",
    ".html",
    ".sql",
    ".sh",
    ".hbs",
    ".tpl",
    ".json",
    ".jsonl",
    ".yml",
    ".yaml",
    ".xml",
    ".properties",
    ".md",
    ".mdx",
    ".mdc",
    ".conf",
    ".cfg",
    ".aql",
    ".hurl",
}

# Docs file extensions (documentation and config)
DOCS_EXTENSIONS = {
    ".md",
    ".mdx",
    ".js",
    ".jsx",
    ".mjs",
    ".json",
    ".yaml",
    ".yml",
    ".css",
    ".sh",
    ".ini",
    ".svg",
    ".txt",
}

SOURCE_EXTENSIONS = {
    "code": REPO_EXTENSIONS,
    "docs": DOCS_EXTENSIONS,
}
SOURCE_DISPLAY_NAMES = {
    "code": "Code",
    "docs": "Documentation",
}

# Union: ingest all supported file types when needed in tests
KNOWN_EXTENSIONS = REPO_EXTENSIONS | DOCS_EXTENSIONS

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100


def _collect_files(sources: list[Path], allowed_extensions: set[str] = KNOWN_EXTENSIONS) -> list[Path]:
    """Return list of readable files under source paths with known extensions."""
    out: list[Path] = []
    for root in sources:
        if not root.exists():
            logger.warning("Knowledge source path does not exist: %s", root)
            continue
        if root.is_file():
            if root.suffix.lower() in allowed_extensions:
                out.append(root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in allowed_extensions:
                out.append(path)
    return out


def _read_text(path: Path) -> str | None:
    """Read file as UTF-8 text; return None if not decodable."""
    try:
        return path.read_text(encoding="utf-8", errors="strict")
    except Exception as e:
        logger.debug("Skip file %s: %s", path, e)
        return None


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks of roughly chunk_size characters."""
    if not text.strip():
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
        if start >= len(text):
            break
    return chunks


def _document_type(path: Path) -> str:
    """Derive document_type from path (e.g. markdown, source, docs)."""
    ext = path.suffix.lower()
    if ext in (".md", ".markdown", ".mdx", ".mdc", ".rst"):
        return "markdown" if ext in (".md", ".markdown", ".mdx", ".mdc") else "rst"
    if ext in (
        ".py",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".cjs",
        ".mjs",
        ".java",
        ".css",
        ".html",
        ".sql",
        ".sh",
        ".json",
        ".jsonl",
        ".xml",
        ".aql",
        ".hurl",
    ):
        return "source"
    if ext in (".yml", ".yaml", ".toml", ".cfg", ".conf", ".ini", ".properties"):
        return "config"
    return "text"


def _get_embeddings(texts: list[str]) -> list[list[float]]:
    """Call OpenAI-compatible embeddings API; returns list of vectors."""
    if not texts:
        return []
    if not config.LLM_API_KEY:
        raise ValueError("LLM_API_KEY (or OPENAI_API_KEY) required for embeddings")
    client = OpenAI(
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL or "https://api.openai.com/v1",
    )
    # Batch to avoid token limits (e.g. 8192 per input)
    batch_size = 50
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(
            input=batch,
            model=config.EMBEDDING_MODEL,
        )
        for d in resp.data:
            all_embeddings.append(d.embedding)
    return all_embeddings


def _fingerprint_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _chunk_file(
    source_key: str,
    path: Path,
    text: str,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> tuple[str, list[dict[str, Any]]]:
    rel_path = str(path)
    doc_type = _document_type(path)
    file_hash = _fingerprint_text(text)
    meta: dict[str, Any] = {
        "filename": path.name,
        "source_key": source_key,
    }
    chunks = [
        {
            "content": raw_chunk,
            "source_path": rel_path,
            "source_key": source_key,
            "file_hash": file_hash,
            "chunk_index": idx,
            "document_type": doc_type,
            "metadata": meta,
        }
        for idx, raw_chunk in enumerate(_chunk_text(text, chunk_size, chunk_overlap))
    ]
    return file_hash, chunks


def _embed_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not chunks:
        return []
    embeddings = _get_embeddings([chunk["content"] for chunk in chunks])
    if len(embeddings) != len(chunks):
        raise RuntimeError(f"Embedding count {len(embeddings)} != chunk count {len(chunks)}")
    for idx, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[idx]
    return chunks


def ingest(source_key: str, *, mode: str = "incremental") -> dict[str, Any]:
    """Ingest one source bucket with incremental fingerprinting by default."""
    if source_key not in SOURCE_EXTENSIONS:
        raise ValueError(f"Unknown knowledge source: {source_key}")

    sources = config.knowledge_sources_by_key.get(source_key, [])
    files = _collect_files(sources, SOURCE_EXTENSIONS[source_key])
    repo = KnowledgeRepository()
    tracked_files = repo.list_tracked_files(source_key)

    if mode == "force":
        delete_all(source_key)
        repo.delete_tracked_files_for_source(source_key)
        tracked_files = {}

    discovered: dict[str, tuple[str, list[dict[str, Any]]]] = {}
    for path in files:
        text = _read_text(path)
        if text is None:
            continue
        discovered[str(path)] = _chunk_file(source_key, path, text)

    files_deleted = 0
    for stale_path in set(tracked_files) - set(discovered):
        delete_file(source_key, stale_path)
        repo.delete_tracked_file(source_key, stale_path)
        files_deleted += 1

    files_processed = 0
    files_skipped_unchanged = 0
    chunks_ingested = 0

    for source_path, (file_hash, chunks) in discovered.items():
        tracked = tracked_files.get(source_path)
        if mode != "force" and tracked and tracked["content_hash"] == file_hash:
            files_skipped_unchanged += 1
            continue

        delete_file(source_key, source_path)
        embedded_chunks = _embed_chunks(chunks)
        if embedded_chunks:
            upsert_chunks(embedded_chunks)
        repo.upsert_tracked_file(source_key, source_path, file_hash, len(embedded_chunks))
        files_processed += 1
        chunks_ingested += len(embedded_chunks)

    return {
        "source_key": source_key,
        "display_name": SOURCE_DISPLAY_NAMES[source_key],
        "chunks_ingested": chunks_ingested,
        "files_processed": files_processed,
        "files_skipped_unchanged": files_skipped_unchanged,
        "files_deleted": files_deleted,
        "embedding_model": config.EMBEDDING_MODEL,
        "embedding_dimension": config.EMBEDDING_DIMENSION,
        "mode": mode,
    }


def search_knowledge(
    query: str,
    limit: int = 10,
    *,
    document_type_filter: str | list[str] | None = None,
    source_filter: str | list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Embed the query and run semantic search; return chunks with content, source_path, metadata.
    document_type_filter: e.g. "source" for repo only, or ["markdown", "text"] for docs only.
    """
    if not query.strip():
        return []
    if not config.LLM_API_KEY:
        logger.warning("LLM_API_KEY not set; cannot embed search query")
        return []
    texts = [query.strip()]
    vectors = _get_embeddings(texts)
    if not vectors:
        return []
    return pg_search(
        vectors[0],
        limit=limit,
        document_type_filter=document_type_filter,
        source_filter=source_filter,
    )
