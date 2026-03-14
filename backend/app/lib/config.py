"""Application config loaded from environment."""

import os
from pathlib import Path


def _str_or_none(value: str | None) -> str | None:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    return value.strip() if isinstance(value, str) else value


def _path_from_env(key: str, default: str | Path) -> Path:
    raw = os.environ.get(key)
    if raw is None or raw.strip() == "":
        return Path(default) if isinstance(default, str) else default
    return Path(raw.strip())


class Config:
    """Configuration from environment. All URLs and paths are read at import/access time."""

    # Loki
    LOKI_URL: str = os.environ.get("LOKI_URL", "http://localhost:3100").strip().rstrip("/")

    # Prometheus
    PROMETHEUS_URL: str = (
        os.environ.get("PROMETHEUS_URL", "http://localhost:9090").strip().rstrip("/")
    )

    # Qdrant
    QDRANT_URL: str = os.environ.get("QDRANT_URL", "http://localhost:6333").strip().rstrip("/")

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

    # Data directory for SQLite and temp extraction
    DATA_DIR: Path = _path_from_env("DATA_DIR", "./data")

    @property
    def db_path(self) -> Path:
        return self.DATA_DIR / "logpilot.db"


# Singleton for app use
config = Config()
