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
    LOKI_PUSH_BATCH_BYTES: int = int(
        os.environ.get("LOKI_PUSH_BATCH_BYTES", str(1 * 1024 * 1024)).strip() or 1048576
    )
    LOKI_PUSH_RATE_LIMIT_BYTES_PER_SEC: int = int(
        os.environ.get("LOKI_PUSH_RATE_LIMIT_BYTES_PER_SEC", "0").strip() or 0
    )
    LOKI_PUSH_MAX_RETRIES: int = int(os.environ.get("LOKI_PUSH_MAX_RETRIES", "2").strip() or 2)
    LOKI_MAX_ENTRY_BYTES: int = int(
        os.environ.get("LOKI_MAX_ENTRY_BYTES", str(256 * 1024)).strip() or 262144
    )

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

    # Knowledge ingest default paths (env: comma-separated paths)
    @staticmethod
    def _split_paths(raw: str) -> list[Path]:
        return [Path(p.strip()) for p in raw.split(",") if p.strip()]

    @property
    def knowledge_code_sources(self) -> list[Path]:
        raw = os.environ.get("KNOWLEDGE_CODE_SOURCES", "").strip()
        return self._split_paths(raw) if raw else []

    @property
    def knowledge_doc_sources(self) -> list[Path]:
        raw = os.environ.get("KNOWLEDGE_DOC_SOURCES", "").strip()
        return self._split_paths(raw) if raw else []

    @property
    def knowledge_sources_by_key(self) -> dict[str, list[Path]]:
        return {
            "code": self.knowledge_code_sources,
            "docs": self.knowledge_doc_sources,
        }


# Singleton for app use
config = Config()
