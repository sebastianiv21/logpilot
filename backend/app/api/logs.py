"""POST /sessions/{session_id}/logs/query — time range, label filters; return log records."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict

from app.lib.loki_client import query_logs
from app.lib.repositories import SessionRepository

router = APIRouter(prefix="/sessions", tags=["sessions", "logs"])
_repo = SessionRepository()


class LogRecordResponse(BaseModel):
    """Single log record from Loki (timestamp_ns, raw_message, plus label keys)."""

    model_config = ConfigDict(extra="allow")

    timestamp_ns: int
    raw_message: str


class LogsQueryResponse(BaseModel):
    """Response for POST /sessions/{session_id}/logs/query."""

    logs: list[LogRecordResponse]


def _parse_iso_to_ns(iso_str: str) -> int:
    """Parse ISO 8601 string to nanoseconds since epoch."""
    from datetime import datetime

    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1_000_000_000)


class LogsQueryBody(BaseModel):
    """Request body: time range and optional label filters."""

    start: str | None = None
    end: str | None = None
    limit: int = 100
    service: str | None = None
    environment: str | None = None
    log_level: str | None = None


@router.post("/{session_id}/logs/query", response_model=LogsQueryResponse)
def query_session_logs(
    session_id: str,
    body: LogsQueryBody | None = None,
) -> LogsQueryResponse:
    """
    Query logs for the session. Body: start, end (ISO 8601), limit, optional label filters.
    Returns log records with timestamp_ns, raw_message, and labels.
    """
    session = _repo.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    body = body or LogsQueryBody()
    start_ns = None
    end_ns = None
    if body.start:
        try:
            start_ns = _parse_iso_to_ns(body.start)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid start time: {e}") from e
    if body.end:
        try:
            end_ns = _parse_iso_to_ns(body.end)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid end time: {e}") from e

    limit = min(max(1, body.limit), 1000)
    label_filters: dict[str, str] = {}
    if body.service:
        label_filters["service"] = body.service.strip()
    if body.environment:
        label_filters["environment"] = body.environment.strip()
    if body.log_level:
        label_filters["log_level"] = body.log_level.strip()

    records = query_logs(
        session_id=session_id,
        start_ns=start_ns,
        end_ns=end_ns,
        label_filters=label_filters or None,
        limit=limit,
    )

    return LogsQueryResponse(
        logs=[LogRecordResponse.model_validate(r) for r in records]
    )
