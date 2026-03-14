"""Chunking and embedding for docs/repo content; coordinates with Qdrant client."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from openai import OpenAI

from app.lib.config import config
from app.lib.qdrant_client import delete_all, upsert_chunks
from app.lib.qdrant_client import search as qdrant_search

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

# Union: ingest both repo and docs file types from any source path
KNOWN_EXTENSIONS = REPO_EXTENSIONS | DOCS_EXTENSIONS

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100


def _collect_files(sources: list[Path]) -> list[Path]:
    """Return list of readable files under source paths with known extensions."""
    out: list[Path] = []
    for root in sources:
        if not root.exists():
            logger.warning("Knowledge source path does not exist: %s", root)
            continue
        if root.is_file():
            if root.suffix.lower() in KNOWN_EXTENSIONS:
                out.append(root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in KNOWN_EXTENSIONS:
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


def chunk_and_embed_sources(
    sources: list[Path],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Discover files under sources, chunk text, produce embeddings. Returns list of
    dicts with content, embedding, source_path, document_type, metadata.
    """
    files = _collect_files(sources)
    if not files:
        logger.warning("No files found under knowledge sources: %s", sources)
        return []

    all_chunks: list[dict[str, Any]] = []
    texts_to_embed: list[str] = []
    chunk_meta: list[tuple[str, str, dict]] = []  # (source_path, document_type, metadata)

    for path in files:
        text = _read_text(path)
        if text is None:
            continue
        try:
            rel_path = str(path)
        except Exception:
            rel_path = path.name
        doc_type = _document_type(path)
        meta: dict[str, Any] = {"filename": path.name}
        for raw_chunk in _chunk_text(text, chunk_size, chunk_overlap):
            all_chunks.append(
                {
                    "content": raw_chunk,
                    "source_path": rel_path,
                    "document_type": doc_type,
                    "metadata": meta,
                }
            )
            texts_to_embed.append(raw_chunk)
            chunk_meta.append((rel_path, doc_type, meta))

    if not texts_to_embed:
        return []

    embeddings = _get_embeddings(texts_to_embed)
    if len(embeddings) != len(all_chunks):
        raise RuntimeError(f"Embedding count {len(embeddings)} != chunk count {len(all_chunks)}")
    for i, ch in enumerate(all_chunks):
        ch["embedding"] = embeddings[i]

    return all_chunks


def ingest(sources: list[Path], *, replace: bool = True) -> dict[str, Any]:
    """
    Ingest sources into Qdrant: chunk, embed, upsert. If replace is True, clear
    collection first (full refresh). Returns summary: chunks_ingested, files_processed.
    """
    if replace:
        delete_all()
    chunks = chunk_and_embed_sources(sources)
    if not chunks:
        return {"chunks_ingested": 0, "files_processed": 0}
    upsert_chunks(chunks)
    files_count = len({c["source_path"] for c in chunks})
    return {"chunks_ingested": len(chunks), "files_processed": files_count}


def search_knowledge(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Embed the query and run semantic search; return chunks with content, source_path, metadata.
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
    return qdrant_search(vectors[0], limit=limit)
