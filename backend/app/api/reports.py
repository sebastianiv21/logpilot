"""Reports API: list, get, generate, export."""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel, Field

from app.lib.config import config
from app.lib.repositories import ReportRepository, SessionRepository
from app.services.agent import generate_incident_report
from app.services.export import export_markdown, export_pdf

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions", "reports"])
_session_repo = SessionRepository()
_report_repo = ReportRepository()


class GenerateReportBody(BaseModel):
    """Body for POST /sessions/{session_id}/reports/generate."""

    question: str = Field(..., min_length=1, description="Natural-language incident question")


class GenerateReportResponse(BaseModel):
    """Response for report generation: id, session_id, created_at, optional content."""

    id: str
    session_id: str
    created_at: str
    content: str | None = None


class ReportListItem(BaseModel):
    """Report in list (no content)."""

    id: str
    session_id: str
    created_at: str


class ReportListResponse(BaseModel):
    """GET /sessions/{session_id}/reports."""

    reports: list[ReportListItem]


class ReportDetailResponse(BaseModel):
    """GET /sessions/{session_id}/reports/{report_id}."""

    id: str
    session_id: str
    content: str
    created_at: str


@router.get("/{session_id}/reports", response_model=ReportListResponse)
def list_reports(session_id: str) -> ReportListResponse:
    """List reports for the session (no content in list)."""
    if _session_repo.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    reports = _report_repo.list_by_session(session_id)
    return ReportListResponse(
        reports=[
            ReportListItem(id=r.id, session_id=r.session_id, created_at=r.created_at)
            for r in reports
        ]
    )


@router.get("/{session_id}/reports/{report_id}", response_model=ReportDetailResponse)
def get_report(session_id: str, report_id: str) -> ReportDetailResponse:
    """Get a single report by id (with content)."""
    report = _report_repo.get_by_id(report_id, session_id=session_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportDetailResponse(
        id=report.id,
        session_id=report.session_id,
        content=report.content,
        created_at=report.created_at,
    )


def _run_report_generation(session_id: str, report_id: str, question: str) -> None:
    """Background task: run agent and update report content; on failure set error in content."""
    repo = ReportRepository()
    try:
        generate_incident_report(
            session_id=session_id,
            question=question,
            report_id=report_id,
        )
    except Exception as e:
        logger.exception("Report generation failed for report_id=%s", report_id)
        error_msg = f"Report generation failed: {e!s}"
        repo.update_content(report_id, session_id, error_msg)


@router.post(
    "/{session_id}/reports/generate",
    response_model=GenerateReportResponse,
    status_code=202,
)
def generate_report(
    session_id: str,
    body: GenerateReportBody,
    background_tasks: BackgroundTasks,
) -> GenerateReportResponse:
    """
    Start incident report generation (async). Returns immediately with report id.
    Poll GET /sessions/{session_id}/reports/{report_id} for content; empty content means still generating.
    """
    if _session_repo.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if not config.LLM_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Report generation unavailable: LLM not configured",
        )
    report = _report_repo.create(session_id=session_id, content="")
    background_tasks.add_task(
        _run_report_generation,
        session_id=session_id,
        report_id=report.id,
        question=body.question,
    )
    return GenerateReportResponse(
        id=report.id,
        session_id=report.session_id,
        created_at=report.created_at,
        content=None,
    )


@router.get("/{session_id}/reports/{report_id}/export")
def export_report(
    session_id: str,
    report_id: str,
    format: str = "markdown",
) -> Response:
    """Export report as Markdown or PDF. Query param: format=markdown|pdf."""
    report = _report_repo.get_by_id(report_id, session_id=session_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    if not (report.content or "").strip():
        raise HTTPException(
            status_code=409,
            detail="Report not yet generated; poll GET .../reports/{report_id} until content is present",
        )
    if format == "markdown":
        content = export_markdown(report.content)
        return PlainTextResponse(content=content, media_type="text/markdown")
    if format == "pdf":
        try:
            pdf_bytes = export_pdf(report.content)
        except RuntimeError as e:
            if "WeasyPrint" in str(e) or "unavailable" in str(e).lower():
                raise HTTPException(
                    status_code=503,
                    detail="PDF export unavailable: install WeasyPrint and its system dependencies",
                ) from e
            raise
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="report-{report_id}.pdf"'},
        )
    raise HTTPException(status_code=400, detail="format must be markdown or pdf")
