"""Application config loaded from environment."""

import os
from pathlib import Path


def _str_or_none(value: str | None) -> str | None:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    return value.strip() if isinstance(value, str) else value


class Config:
    """Configuration from environment. All values are read at import/access time."""

    # Loki
    LOKI_URL: str = os.environ.get("LOKI_URL", "http://localhost:3100").strip().rstrip("/")

    # Prometheus
    PROMETHEUS_URL: str = (
        os.environ.get("PROMETHEUS_URL", "http://localhost:9090").strip().rstrip("/")
    )

    # PostgreSQL (required — replaces QDRANT_URL and DATA_DIR/SQLite)
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "").strip()

    # LLM (OpenAI-compatible)
    LLM_BASE_URL: str | None = _str_or_none(os.environ.get("LLM_BASE_URL"))
    LLM_API_KEY: str | None = _str_or_none(os.environ.get("LLM_API_KEY"))
    LLM_MODEL: str = (os.environ.get("LLM_MODEL") or "gpt-4o-mini").strip()

    # Embeddings (OpenAI-compatible; same base URL as LLM)
    EMBEDDING_MODEL: str = (os.environ.get("EMBEDDING_MODEL") or "text-embedding-3-small").strip()
    EMBEDDING_DIMENSION: int = int(os.environ.get("EMBEDDING_DIMENSION", "1536").strip() or "1536")

    # Knowledge ingest default paths (env KNOWLEDGE_SOURCES: comma-separated paths)
    @property
    def knowledge_sources(self) -> list[Path]:
        raw = os.environ.get("KNOWLEDGE_SOURCES", "").strip()
        if not raw:
            return []
        return [Path(p.strip()) for p in raw.split(",") if p.strip()]


# Singleton for app use
config = Config()
