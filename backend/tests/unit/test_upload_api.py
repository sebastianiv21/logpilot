"""Unit tests for upload API edge cases."""

from __future__ import annotations

from io import BytesIO

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from app.api import upload as upload_api


@pytest.mark.anyio
async def test_upload_logs_rejects_reupload_when_session_already_has_logs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(upload_api._repo, "get", lambda session_id: {"id": session_id})
    monkeypatch.setattr(upload_api._repo, "get_log_extent", lambda session_id: (1, 2))
    monkeypatch.setattr(upload_api._repo, "get_upload_summary", lambda session_id: None)

    file = UploadFile(filename="logs.zip", file=BytesIO(b"unused"))

    with pytest.raises(HTTPException) as exc_info:
        await upload_api.upload_logs("session-1", file)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == (
        "This session already has logs. Create a new session to upload another archive."
    )


@pytest.mark.anyio
async def test_upload_logs_runs_retention_cleanup_after_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    summary_calls = {"count": 0}
    monkeypatch.setattr(upload_api._repo, "get", lambda session_id: {"id": session_id})
    monkeypatch.setattr(upload_api._repo, "get_log_extent", lambda session_id: None)
    monkeypatch.setattr(
        upload_api,
        "run_upload_pipeline",
        lambda zip_path, session_id: upload_api.UploadResultResponse(
            status="success",
            files_processed=1,
            files_skipped=0,
            lines_parsed=10,
            lines_rejected=0,
            session_id=session_id,
            error=None,
        ),
    )
    monkeypatch.setattr(
        upload_api._repo,
        "upsert_upload_summary",
        lambda **kwargs: None,
    )
    def fake_get_upload_summary(session_id: str):
        summary_calls["count"] += 1
        if summary_calls["count"] == 1:
            return None
        return {
            "status": "success",
            "files_processed": 1,
            "files_skipped": 0,
            "lines_parsed": 10,
            "lines_rejected": 0,
            "session_id": session_id,
            "error": None,
            "uploaded_file_name": "logs.zip",
            "updated_at": "2026-04-03T10:00:00Z",
        }

    monkeypatch.setattr(upload_api._repo, "get_upload_summary", fake_get_upload_summary)

    async def fake_to_thread(func, *args, **kwargs):
        calls.append(func.__name__)
        return func(*args, **kwargs)

    monkeypatch.setattr(upload_api.asyncio, "to_thread", fake_to_thread)
    monkeypatch.setattr(upload_api, "run_session_retention_cleanup", lambda: calls.append("cleanup"))

    file = UploadFile(filename="logs.zip", file=BytesIO(b"test"))
    await upload_api.upload_logs("session-1", file)

    assert "cleanup" in calls
