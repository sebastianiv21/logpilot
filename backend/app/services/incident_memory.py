"""Cross-session incident memory: index completed reports, surface prior matches.

After a report finishes, ``index_report`` embeds a composed "fingerprint"
(summary + root cause + evidence — NOT the full markdown, which is noisy) and
upserts it into the configured VectorStore with ``document_type='report'``.

The agent can later call ``search_past_incidents`` to ask "have we seen this
before?" — the lookup excludes the current session via the
``exclude_session_id`` filter so the agent doesn't recommend itself.

Both functions degrade gracefully when embeddings are unavailable: indexing
logs a warning and returns; search returns ``[]``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.lib.embeddings import EmbeddingsUnavailableError, embed_text
from app.lib.vector_store import Chunk, VectorSearchFilters, get_vector_store
from app.services.report_model import IncidentReport

logger = logging.getLogger(__name__)

REPORT_DOCUMENT_TYPE = "report"
REPORT_SOURCE_KEY = "incident_reports"


@dataclass(frozen=True)
class PastIncident:
    """One previously-investigated incident, surfaced to the agent."""

    session_id: str
    report_id: str
    question: str
    summary: str
    root_cause: str
    created_at: str
    similarity: float


def build_fingerprint(report: IncidentReport) -> str:
    """Compose the text we embed for similarity search.

    Concatenates the most discriminating fields: summary, root cause, and the
    evidence descriptions. Skips noisier fields (recommended_fix,
    troubleshooting_steps, coding_agent_fix_prompt) so two reports about the
    same incident come out close in embedding space.
    """
    parts: list[str] = [
        report.incident_summary.strip(),
        report.possible_root_cause.strip(),
    ]
    for item in report.supporting_evidence:
        desc = item.description.strip()
        if desc:
            parts.append(f"({item.source}) {desc}")
    return "\n".join(p for p in parts if p)


def build_fingerprint_from_markdown(content: str) -> str:
    """Same intent as :func:`build_fingerprint`, but pulls the sections out of
    rendered markdown — used by the backfill script for already-persisted
    reports that we never had as ``IncidentReport`` instances.

    Recognised section headers come from
    :data:`app.services.report_model.REPORT_SECTIONS`. We keep just the first
    three (summary, root cause, supporting evidence)."""
    import re

    wanted = {
        "Incident Summary",
        "Possible Root Cause",
        "Supporting Evidence",
    }
    # Match "## Name\n<body>" up to the next "## " or end-of-string.
    pattern = re.compile(
        r"^##\s+(?P<name>[^\n]+)\n(?P<body>.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    parts: list[str] = []
    for match in pattern.finditer(content):
        name = match.group("name").strip()
        if name in wanted:
            body = match.group("body").strip()
            if body and body != "*Not determined.*":
                parts.append(body)
    return "\n".join(parts)


def index_report(
    *,
    session_id: str,
    report_id: str,
    question: str,
    created_at: str,
    report: IncidentReport,
) -> bool:
    """Embed the report's fingerprint and upsert it into the vector store.

    Returns True on success, False on degradation (embeddings unavailable,
    backend write failed). Never raises — call from a post-success path
    where indexing failure must not break the user-visible report.
    """
    fingerprint = build_fingerprint(report)
    if not fingerprint:
        logger.info(
            "Skipping incident-memory index for report_id=%s — empty fingerprint",
            report_id,
        )
        return False

    try:
        embedding = embed_text(fingerprint)
    except EmbeddingsUnavailableError as exc:
        logger.warning(
            "Skipping incident-memory index for report_id=%s (%s)", report_id, exc
        )
        return False
    except Exception:
        logger.exception(
            "Failed to embed fingerprint for incident-memory index (report_id=%s)",
            report_id,
        )
        return False

    chunk: Chunk = {
        "content": fingerprint,
        "embedding": embedding,
        "source_key": REPORT_SOURCE_KEY,
        "source_path": f"reports/{report_id}",
        "document_type": REPORT_DOCUMENT_TYPE,
        "chunk_index": 0,
        "metadata": {
            "session_id": session_id,
            "report_id": report_id,
            "question": question,
            "created_at": created_at,
            "summary": report.incident_summary.strip(),
            "root_cause": report.possible_root_cause.strip(),
        },
    }
    try:
        store = get_vector_store()
        # Replace any prior chunk for this report (covers re-runs against the
        # same report_id, e.g. background regeneration).
        store.delete(source_key=REPORT_SOURCE_KEY, source_path=f"reports/{report_id}")
        store.upsert([chunk])
    except Exception:
        logger.exception(
            "Failed to upsert incident-memory chunk for report_id=%s", report_id
        )
        return False

    logger.info(
        "Indexed incident memory: session_id=%s report_id=%s chars=%d",
        session_id,
        report_id,
        len(fingerprint),
    )
    return True


def index_existing_report_content(
    *,
    session_id: str,
    report_id: str,
    question: str,
    created_at: str,
    content: str,
) -> bool:
    """Backfill path: index a previously-persisted report from its markdown.

    Uses :func:`build_fingerprint_from_markdown` to skip the structured-model
    reconstruction. Same return semantics as :func:`index_report`.
    """
    fingerprint = build_fingerprint_from_markdown(content)
    if not fingerprint:
        logger.info(
            "Backfill: empty fingerprint for report_id=%s, skipping", report_id
        )
        return False
    try:
        embedding = embed_text(fingerprint)
    except EmbeddingsUnavailableError as exc:
        logger.warning("Backfill: skipping report_id=%s (%s)", report_id, exc)
        return False
    except Exception:
        logger.exception("Backfill: embed failed for report_id=%s", report_id)
        return False

    summary, root_cause = _extract_summary_and_root_cause(content)
    chunk: Chunk = {
        "content": fingerprint,
        "embedding": embedding,
        "source_key": REPORT_SOURCE_KEY,
        "source_path": f"reports/{report_id}",
        "document_type": REPORT_DOCUMENT_TYPE,
        "chunk_index": 0,
        "metadata": {
            "session_id": session_id,
            "report_id": report_id,
            "question": question,
            "created_at": created_at,
            "summary": summary,
            "root_cause": root_cause,
        },
    }
    try:
        store = get_vector_store()
        store.delete(source_key=REPORT_SOURCE_KEY, source_path=f"reports/{report_id}")
        store.upsert([chunk])
    except Exception:
        logger.exception("Backfill: upsert failed for report_id=%s", report_id)
        return False
    return True


def _extract_summary_and_root_cause(content: str) -> tuple[str, str]:
    """Pull the first lines of the Summary and Root Cause sections out of
    rendered markdown for use as PastIncident metadata. Returns ('', '') if
    a section is missing."""
    import re

    pattern = re.compile(
        r"^##\s+(?P<name>[^\n]+)\n(?P<body>.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    out = {"Incident Summary": "", "Possible Root Cause": ""}
    for match in pattern.finditer(content):
        name = match.group("name").strip()
        if name in out:
            body = match.group("body").strip()
            if body and body != "*Not determined.*":
                out[name] = body
    return out["Incident Summary"], out["Possible Root Cause"]


def search_past_incidents(
    query: str,
    *,
    current_session_id: str,
    limit: int = 5,
    min_similarity: float = 0.75,
) -> list[PastIncident]:
    """Find prior incident reports semantically similar to ``query``.

    Excludes ``current_session_id`` from results. Filters by
    ``min_similarity`` (cosine, higher is more similar). Returns empty list
    when embeddings are unavailable or the store has no matching chunks.
    """
    if not query.strip():
        return []
    try:
        embedding = embed_text(query.strip())
    except EmbeddingsUnavailableError as exc:
        logger.warning("search_past_incidents unavailable: %s", exc)
        return []
    except Exception:
        logger.exception("search_past_incidents failed to embed query")
        return []

    filters: VectorSearchFilters = {
        "document_type": REPORT_DOCUMENT_TYPE,
        "source_key": REPORT_SOURCE_KEY,
        "exclude_session_id": current_session_id,
    }
    try:
        chunks = get_vector_store().search(
            embedding, limit=max(1, limit), filters=filters
        )
    except Exception:
        logger.exception("search_past_incidents failed on vector store search")
        return []

    out: list[PastIncident] = []
    for chunk in chunks:
        score = float(chunk.get("score", 0.0))
        if score < min_similarity:
            continue
        meta: dict[str, Any] = chunk.get("metadata") or {}
        out.append(
            PastIncident(
                session_id=str(meta.get("session_id") or ""),
                report_id=str(meta.get("report_id") or ""),
                question=str(meta.get("question") or ""),
                summary=str(meta.get("summary") or ""),
                root_cause=str(meta.get("root_cause") or ""),
                created_at=str(meta.get("created_at") or ""),
                similarity=score,
            )
        )
    return out
