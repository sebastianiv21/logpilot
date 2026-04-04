"""Reports API: list, get, generate, export."""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse, Response, StreamingResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from app.lib.config import config
from app.lib.repositories import ReportRepository, SessionRepository
from app.services.agent import generate_incident_report
from app.services.export import (
    PDFExportRenderError,
    PDFExportTooLargeError,
    export_markdown,
    export_pdf_to_file,
    iter_pdf_chunks,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions", "reports"])
_session_repo = SessionRepository()
_report_repo = ReportRepository()
PDF_EXPORT_FAILURE_DETAIL = "PDF export failed. Please try again or use Markdown export."


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
    question_preview: str | None = None
    has_question: bool


class ReportListResponse(BaseModel):
    """GET /sessions/{session_id}/reports."""

    reports: list[ReportListItem]


class ReportDetailResponse(BaseModel):
    """GET /sessions/{session_id}/reports/{report_id}."""

    id: str
    session_id: str
    content: str
    question: str | None = None
    created_at: str


@router.get("/{session_id}/reports", response_model=ReportListResponse)
def list_reports(session_id: str) -> ReportListResponse:
    """List reports for the session (no content in list)."""
    if _session_repo.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    reports = _report_repo.list_by_session(session_id)
    return ReportListResponse(
        reports=[
            ReportListItem(
                id=r.id,
                session_id=r.session_id,
                created_at=r.created_at,
                question_preview=_report_repo.question_preview(r.question),
                has_question=r.question is not None,
            )
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
        question=report.question,
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


def _log_pdf_export(report_id: str, outcome: str, **fields: object) -> None:
    logger.info(
        "pdf_export report_id=%s outcome=%s %s",
        report_id,
        outcome,
        " ".join(f"{key}={value}" for key, value in fields.items()),
    )


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
    Poll GET /sessions/{session_id}/reports/{report_id} for content;
    empty content means still generating.
    """
    if _session_repo.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Incident question cannot be empty")
    if not config.LLM_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Report generation unavailable: LLM not configured",
        )
    report = _report_repo.create(session_id=session_id, content="", question=question)
    background_tasks.add_task(
        _run_report_generation,
        session_id=session_id,
        report_id=report.id,
        question=question,
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
            detail=(
                "Report not yet generated; poll GET .../reports/{report_id} "
                "until content is present"
            ),
        )
    if format == "markdown":
        content = export_markdown(report.content)
        return PlainTextResponse(content=content, media_type="text/markdown")
    if format == "pdf":
        try:
            result = export_pdf_to_file(report.content)
        except PDFExportTooLargeError as e:
            _log_pdf_export(
                report_id,
                "rejected",
                report_chars=e.stats.report_chars,
                code_fence_count=e.stats.code_fence_count,
                code_block_line_count=e.stats.code_block_line_count,
                block_count=e.stats.block_count,
                flowable_count=e.stats.flowable_count,
                duration_ms=f"{e.stats.duration_ms:.2f}",
                rss_kb_before=e.stats.rss_kb_before,
                rss_kb_after=e.stats.rss_kb_after,
            )
            raise HTTPException(status_code=413, detail=e.detail) from e
        except PDFExportRenderError as e:
            _log_pdf_export(
                report_id,
                "failed",
                report_chars=e.stats.report_chars,
                code_fence_count=e.stats.code_fence_count,
                code_block_line_count=e.stats.code_block_line_count,
                block_count=e.stats.block_count,
                flowable_count=e.stats.flowable_count,
                duration_ms=f"{e.stats.duration_ms:.2f}",
                rss_kb_before=e.stats.rss_kb_before,
                rss_kb_after=e.stats.rss_kb_after,
            )
            logger.exception("PDF export failed for report_id=%s", report_id)
            raise HTTPException(
                status_code=503,
                detail=PDF_EXPORT_FAILURE_DETAIL,
            ) from e
        _log_pdf_export(
            report_id,
            "success",
            report_chars=result.stats.report_chars,
            code_fence_count=result.stats.code_fence_count,
            code_block_line_count=result.stats.code_block_line_count,
            block_count=result.stats.block_count,
            flowable_count=result.stats.flowable_count,
            duration_ms=f"{result.stats.duration_ms:.2f}",
            rss_kb_before=result.stats.rss_kb_before,
            rss_kb_after=result.stats.rss_kb_after,
            output_bytes=result.stats.output_bytes,
        )
        return StreamingResponse(
            iter_pdf_chunks(result.file),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="report-{report_id}.pdf"'},
            background=BackgroundTask(result.file.close),
        )
    raise HTTPException(status_code=400, detail="format must be markdown or pdf")
