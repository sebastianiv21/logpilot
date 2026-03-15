"""POST /sessions/{session_id}/logs/upload — multipart file; 413/400/404 per contract."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.lib.repositories import SessionRepository
from app.services.upload import MAX_COMPRESSED_BYTES, run_upload_pipeline

CHUNK_SIZE = 1024 * 1024  # 1 MiB

router = APIRouter(prefix="/sessions", tags=["sessions", "upload"])
_repo = SessionRepository()


class UploadResultResponse(BaseModel):
    """Response for POST /sessions/{session_id}/logs/upload."""

    status: str
    files_processed: int
    files_skipped: int
    lines_parsed: int
    lines_rejected: int
    session_id: str
    error: str | None = None
    uploaded_file_name: str | None = None
    updated_at: str | None = None


@router.get(
    "/{session_id}/upload-summary",
    response_model=UploadResultResponse,
    summary="Get last upload summary for session",
)
def get_upload_summary(session_id: str) -> UploadResultResponse:
    """
    Return the last upload result for the session (for display after refresh).
    404 if session not found or session has never had an upload.
    """
    if _repo.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    summary = _repo.get_upload_summary(session_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="No upload summary for this session")
    return UploadResultResponse(
        status=summary["status"],
        files_processed=summary["files_processed"],
        files_skipped=summary["files_skipped"],
        lines_parsed=summary["lines_parsed"],
        lines_rejected=summary["lines_rejected"],
        session_id=summary["session_id"],
        error=summary["error"],
        uploaded_file_name=summary.get("uploaded_file_name"),
        updated_at=summary.get("updated_at"),
    )


@router.post("/{session_id}/logs/upload", response_model=UploadResultResponse)
async def upload_logs(
    session_id: str,
    file: UploadFile = File(..., alias="file"),  # noqa: B008
) -> UploadResultResponse:
    """
    Upload a compressed log archive for the session. Returns upload result (status, counts, error).
    404 if session not found; 413 if too large; 400 on validation/malformed archive.
    """
    session = _repo.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file: expected a .zip archive",
        )

    fd, tmp = tempfile.mkstemp(suffix=".zip")
    zip_path = Path(tmp)
    try:
        total = 0
        with open(fd, "wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                total += len(chunk)
                if total > MAX_COMPRESSED_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Archive exceeds limit ({MAX_COMPRESSED_BYTES} bytes / 100 MB)",
                    )
                out.write(chunk)

        result = await asyncio.to_thread(run_upload_pipeline, zip_path, session_id)
    finally:
        zip_path.unlink(missing_ok=True)

    if result.status == "failed" and result.error:
        err = result.error
        if "exceeds limit" in err:
            raise HTTPException(status_code=413, detail=err)
        if "path traversal" in err.lower():
            raise HTTPException(status_code=400, detail=err)

    _repo.upsert_upload_summary(
        session_id=session_id,
        status=result.status,
        files_processed=result.files_processed,
        files_skipped=result.files_skipped,
        lines_parsed=result.lines_parsed,
        lines_rejected=result.lines_rejected,
        error=result.error,
        uploaded_file_name=file.filename,
    )
    updated = _repo.get_upload_summary(session_id)

    return UploadResultResponse(
        status=result.status,
        files_processed=result.files_processed,
        files_skipped=result.files_skipped,
        lines_parsed=result.lines_parsed,
        lines_rejected=result.lines_rejected,
        session_id=result.session_id,
        error=result.error,
        uploaded_file_name=file.filename,
        updated_at=updated["updated_at"] if updated else None,
    )
