"""Application config loaded from environment."""

import os
from pathlib import Path


def _str_or_none(value: str | None) -> str | None:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    return value.strip() if isinstance(value, str) else value


class Config:
    """Configuration from environment. All values are read at import/access time."""

    def __init__(self) -> None:
        # Loki
        self.LOKI_URL: str = os.environ.get("LOKI_URL", "http://localhost:3100").strip().rstrip("/")
        self.LOKI_PUSH_BATCH_BYTES: int = int(
            os.environ.get("LOKI_PUSH_BATCH_BYTES", str(1 * 1024 * 1024)).strip() or 1048576
        )
        self.LOKI_PUSH_RATE_LIMIT_BYTES_PER_SEC: int = int(
            os.environ.get("LOKI_PUSH_RATE_LIMIT_BYTES_PER_SEC", "0").strip() or 0
        )
        self.LOKI_PUSH_MAX_RETRIES: int = int(
            os.environ.get("LOKI_PUSH_MAX_RETRIES", "2").strip() or 2
        )
        self.LOKI_MAX_ENTRY_BYTES: int = int(
            os.environ.get("LOKI_MAX_ENTRY_BYTES", str(256 * 1024)).strip() or 262144
        )
        # Prometheus
        self.PROMETHEUS_URL: str = (
            os.environ.get("PROMETHEUS_URL", "http://localhost:9090").strip().rstrip("/")
        )
        self.PROMETHEUS_RETENTION_TIME: str = (
            os.environ.get("PROMETHEUS_RETENTION_TIME", "30d").strip() or "30d"
        )

        # PostgreSQL
        self.DATABASE_URL: str = os.environ.get("DATABASE_URL", "").strip()

        # LLM / embeddings
        self.LLM_BASE_URL: str | None = _str_or_none(os.environ.get("LLM_BASE_URL"))
        self.LLM_API_KEY: str | None = _str_or_none(os.environ.get("LLM_API_KEY"))
        self.LLM_MODEL: str = (os.environ.get("LLM_MODEL") or "gpt-4o-mini").strip()
        self.EMBEDDING_MODEL: str = (
            os.environ.get("EMBEDDING_MODEL") or "text-embedding-3-small"
        ).strip()
        self.EMBEDDING_DIMENSION: int = int(
            os.environ.get("EMBEDDING_DIMENSION", "1536").strip() or "1536"
        )

        # Vector parser sidecar (dual-write).
        # Backend drops extracted log files at:
        #   <VECTOR_LOG_DROP_DIR>/<session_id>/<service>/<filename>
        # so the Vector container can pick them up. Empty disables the drop.
        self.VECTOR_LOG_DROP_DIR: str = (
            os.environ.get("VECTOR_LOG_DROP_DIR") or ""
        ).strip()
        # Python pipeline pushes are tagged with this Loki label so queries can
        # distinguish them from the Vector sidecar's pushes.
        self.LOKI_PARSER_LABEL: str = (
            os.environ.get("LOKI_PARSER_LABEL") or "python"
        ).strip()
        # Default `parser` label that query_logs filters on. Flip to "vector"
        # during cutover; queries explicitly passing parser= override this.
        self.LOKI_QUERY_PARSER: str = (
            os.environ.get("LOKI_QUERY_PARSER") or "python"
        ).strip()

        # Session retention
        self.SESSION_RETENTION_ENABLED: bool = (
            os.environ.get("SESSION_RETENTION_ENABLED", "true").strip().lower()
            not in {"0", "false", "no"}
        )
        self.SESSION_RETENTION_MAX_COUNT: int = int(
            os.environ.get("SESSION_RETENTION_MAX_COUNT", "20").strip() or "20"
        )
        self.SESSION_RETENTION_MAX_AGE_DAYS: int = int(
            os.environ.get("SESSION_RETENTION_MAX_AGE_DAYS", "30").strip() or "30"
        )

    # Knowledge ingest default paths (env: comma-separated paths)
    @staticmethod
    def _split_paths(raw: str) -> list[Path]:
        return [Path(p.strip()) for p in raw.split(",") if p.strip()]

    @property
    def knowledge_code_sources(self) -> list[Path]:
        """Allowlist for on-demand code search (grep_repo, read_file).

        These paths are NOT pre-indexed or embedded; they bound what the agent's
        ripgrep-based tools are allowed to reach at query time.
        """
        raw = os.environ.get("KNOWLEDGE_CODE_SOURCES", "").strip()
        return self._split_paths(raw) if raw else []

    @property
    def knowledge_doc_sources(self) -> list[Path]:
        raw = os.environ.get("KNOWLEDGE_DOC_SOURCES", "").strip()
        return self._split_paths(raw) if raw else []

    @property
    def knowledge_sources_by_key(self) -> dict[str, list[Path]]:
        """Ingestable knowledge sources (docs only; code is queried on demand)."""
        return {
            "docs": self.knowledge_doc_sources,
        }


# Singleton for app use
config = Config()
