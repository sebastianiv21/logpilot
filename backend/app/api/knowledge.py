"""POST /knowledge/ingest and POST /knowledge/search — repeatable ingestion and semantic search."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import BackgroundTasks, APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.lib.config import config
from app.services import knowledge as knowledge_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# In-memory state for async ingest (avoids long-running request timeouts)
_ingest_running = False
_ingest_last_result: dict | None = None
_ingest_error: str | None = None


class IngestRequest(BaseModel):
    """Optional list of source paths; if empty, config KNOWLEDGE_SOURCES is used."""

    sources: list[str] = Field(default_factory=list, description="Paths to docs/repo roots")


class IngestResponse(BaseModel):
    """Response for POST /knowledge/ingest (sync or 202 body)."""

    chunks_ingested: int
    files_processed: int


class IngestAcceptedResponse(BaseModel):
    """Response when ingest is started in background (202)."""

    message: str = "Ingest started in background; may take several minutes. Poll GET /knowledge/ingest/status for result."


class SearchRequest(BaseModel):
    """Body for POST /knowledge/search."""

    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max chunks to return")


class ChunkResult(BaseModel):
    """Single chunk in search results."""

    content: str
    source_path: str
    metadata: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Response for POST /knowledge/search."""

    chunks: list[ChunkResult]


def _run_ingest(sources: list[Path]) -> None:
    global _ingest_running, _ingest_last_result, _ingest_error
    try:
        result = knowledge_service.ingest(sources, replace=True)
        _ingest_last_result = result
        _ingest_error = None
    except Exception as e:
        logger.exception("Background ingest failed")
        _ingest_error = str(e)
        _ingest_last_result = None
    finally:
        _ingest_running = False


@router.post(
    "/ingest",
    response_model=IngestAcceptedResponse,
    status_code=202,
    summary="Start knowledge ingest (async)",
)
def ingest_knowledge(body: IngestRequest, background_tasks: BackgroundTasks) -> IngestAcceptedResponse:
    """
    Start ingestion in the background. Ingest can take several minutes (many embedding
    API calls). Returns immediately; poll GET /knowledge/ingest/status for progress and result.
    """
    global _ingest_running
    if body.sources:
        sources = [Path(p) for p in body.sources]
    else:
        sources = config.knowledge_sources
    if not sources:
        raise HTTPException(
            status_code=400,
            detail="No sources provided and KNOWLEDGE_SOURCES not configured",
        )
    if not config.LLM_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Embeddings unavailable: LLM_API_KEY not set",
        )
    if _ingest_running:
        raise HTTPException(
            status_code=409,
            detail="Ingest already in progress; poll GET /knowledge/ingest/status",
        )
    _ingest_running = True
    background_tasks.add_task(_run_ingest, sources)
    return IngestAcceptedResponse()


class IngestStatusResponse(BaseModel):
    """Status of the last or current ingest."""

    status: str = Field(..., description="running | idle")
    last_result: IngestResponse | None = Field(None, description="Result of last completed ingest")
    error: str | None = Field(None, description="Error message if last run failed")


@router.get("/ingest/status", response_model=IngestStatusResponse)
def ingest_status() -> IngestStatusResponse:
    """Return whether ingest is running and the result of the last completed run."""
    last = None
    if _ingest_last_result is not None:
        last = IngestResponse(
            chunks_ingested=_ingest_last_result["chunks_ingested"],
            files_processed=_ingest_last_result["files_processed"],
        )
    return IngestStatusResponse(
        status="running" if _ingest_running else "idle",
        last_result=last,
        error=_ingest_error,
    )


@router.post("/search", response_model=SearchResponse)
def search_knowledge(body: SearchRequest) -> SearchResponse:
    """
    Semantic search over the knowledge base. Returns chunks with content, source_path, metadata.
    """
    if not config.LLM_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Search unavailable: LLM_API_KEY not set",
        )
    chunks = knowledge_service.search_knowledge(query=body.query, limit=body.limit)
    return SearchResponse(
        chunks=[
            ChunkResult(
                content=c["content"],
                source_path=c["source_path"],
                metadata=c.get("metadata", {}),
            )
            for c in chunks
        ],
    )
