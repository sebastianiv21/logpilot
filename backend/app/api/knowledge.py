"""Knowledge ingest/search API with persisted per-source status."""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from app.lib.config import config
from app.lib.repositories import KnowledgeRepository
from app.services import knowledge as knowledge_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge", tags=["knowledge"])
knowledge_repo = KnowledgeRepository()


class IngestRequest(BaseModel):
    """Request body for starting ingest of one configured source.

    Source code is no longer ingested; use grep_repo / read_file agent tools
    instead. Only documentation flows through the embeddings pipeline now.
    """

    source: Literal["docs"] = Field(..., description="Knowledge source to ingest")
    mode: Literal["incremental", "force"] = Field(
        default="incremental",
        description="Incremental skips unchanged files; force refreshes the selected source",
    )


class IngestAcceptedResponse(BaseModel):
    """Response when ingest is started in background (202)."""

    message: str = (
        "Ingest started in background; may take several minutes. "
        "Poll GET /knowledge/sources/status for result."
    )


class SearchRequest(BaseModel):
    """Body for POST /knowledge/search."""

    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max chunks to return")
    source_filter: Literal["all", "docs"] = Field(
        default="all",
        description="Filter results to one knowledge source or search all",
    )


class ChunkResult(BaseModel):
    """Single chunk in search results."""

    content: str
    source_path: str
    source_key: str
    metadata: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response for POST /knowledge/search."""

    chunks: list[ChunkResult]


class KnowledgeSourceStatus(BaseModel):
    """Persisted status for one knowledge source."""

    source_key: Literal["docs"]
    display_name: str
    configured_paths: list[str]
    status: Literal["idle", "running", "ready", "failed"]
    last_started_at: str | None = None
    last_completed_at: str | None = None
    last_error: str | None = None
    last_chunks_ingested: int = 0
    last_files_processed: int = 0
    last_files_skipped_unchanged: int = 0
    last_files_deleted: int = 0
    last_embedding_model: str | None = None
    last_embedding_dimension: int | None = None
    last_ingest_mode: Literal["incremental", "force"] | None = None


class KnowledgeSourcesStatusResponse(BaseModel):
    """Response for GET /knowledge/sources/status."""

    sources: list[KnowledgeSourceStatus]


def _run_ingest(source_key: str, mode: str) -> None:
    try:
        result = knowledge_service.ingest(source_key, mode=mode)
        knowledge_repo.mark_completed(source_key, result)
    except Exception as exc:
        logger.exception("Background ingest failed")
        knowledge_repo.mark_failed(source_key, str(exc), mode)


@router.post(
    "/ingest",
    response_model=IngestAcceptedResponse,
    status_code=202,
    summary="Start knowledge ingest (async)",
)
def ingest_knowledge(body: IngestRequest, background_tasks: BackgroundTasks) -> IngestAcceptedResponse:
    """Start one source ingest in the background."""
    source = knowledge_repo.get_source(body.source)
    if source is None:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    if not source["configured_paths"]:
        raise HTTPException(
            status_code=400,
            detail=f"No configured paths for knowledge source '{body.source}'",
        )
    if not config.LLM_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Embeddings unavailable: LLM_API_KEY not set",
        )
    if source["status"] == "running":
        raise HTTPException(
            status_code=409,
            detail=f"Ingest already in progress for '{body.source}'",
        )
    knowledge_repo.mark_started(body.source, body.mode)
    background_tasks.add_task(_run_ingest, body.source, body.mode)
    return IngestAcceptedResponse()


@router.get("/sources/status", response_model=KnowledgeSourcesStatusResponse)
def sources_status() -> KnowledgeSourcesStatusResponse:
    """Return status for all configured knowledge sources."""
    return KnowledgeSourcesStatusResponse(
        sources=[KnowledgeSourceStatus(**source) for source in knowledge_repo.list_sources()]
    )


@router.post("/search", response_model=SearchResponse)
def search_knowledge(body: SearchRequest) -> SearchResponse:
    """Semantic search over the knowledge base."""
    if not config.LLM_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Search unavailable: LLM_API_KEY not set",
        )
    source_filter = None if body.source_filter == "all" else body.source_filter
    chunks = knowledge_service.search_knowledge(
        query=body.query,
        limit=body.limit,
        source_filter=source_filter,
    )
    return SearchResponse(
        chunks=[
            ChunkResult(
                content=chunk["content"],
                source_path=chunk["source_path"],
                source_key=chunk.get("source_key", ""),
                metadata=chunk.get("metadata", {}),
            )
            for chunk in chunks
        ],
    )
