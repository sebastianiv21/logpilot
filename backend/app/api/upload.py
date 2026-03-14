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

    return UploadResultResponse(
        status=result.status,
        files_processed=result.files_processed,
        files_skipped=result.files_skipped,
        lines_parsed=result.lines_parsed,
        lines_rejected=result.lines_rejected,
        session_id=result.session_id,
        error=result.error,
    )
