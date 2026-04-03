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
