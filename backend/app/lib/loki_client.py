"""Loki query and delete client. Pushing is done by the Vector sidecar."""

from __future__ import annotations

import time
from datetime import UTC, datetime

import httpx

from app.lib.config import config

LOKI_QUERY_RANGE_PATH = "/loki/api/v1/query_range"
LOKI_DELETE_PATH = "/loki/api/v1/delete"


def query_logs(
    *,
    session_id: str,
    start_ns: int | None = None,
    end_ns: int | None = None,
    label_filters: dict[str, str] | None = None,
    limit: int = 100,
    direction: str | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> list[dict]:
    """
    Query Loki for log lines: session_id required; optional time range (ns) and label filters.
    Returns list of records: timestamp_ns, raw_message, and label keys.
    direction: 'forward' (oldest first) or 'backward' (newest first); optional.
    """
    parts = [f'session_id="{session_id}"']
    effective_filters = dict(label_filters or {})
    for k, v in effective_filters.items():
        if v:
            parts.append(f'{k}="{v}"')
    logql = "{" + ", ".join(parts) + "}"
    params: dict[str, str | int] = {"query": logql, "limit": limit}
    if start_ns is not None:
        params["start"] = start_ns
    if end_ns is not None:
        params["end"] = end_ns
    if direction is not None and direction in ("forward", "backward"):
        params["direction"] = direction

    url = (base_url or config.LOKI_URL).rstrip("/") + LOKI_QUERY_RANGE_PATH
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
    data = resp.json()
    result: list[dict] = []
    for stream in data.get("data", {}).get("result", []):
        labels = stream.get("stream", {})
        for ts_ns, line in stream.get("values", []):
            result.append(
                {
                    "timestamp_ns": int(ts_ns),
                    "raw_message": line,
                    **labels,
                }
            )
    return result


def get_log_time_range_ns(
    *,
    session_id: str,
    label_filters: dict[str, str] | None = None,
    base_url: str | None = None,
    timeout: float = 10.0,
) -> tuple[int, int] | None:
    """
    Return (min_ts_ns, max_ts_ns) for the session's logs, or None if no logs.
    Uses a wide time range (epoch to now) and two queries: forward limit=1 for
    oldest, backward limit=1 for newest. Falls back to single query if direction
    is not supported by the Loki server.
    """
    end_ns = int(time.time() * 1_000_000_000)
    start_ns = 0

    try:
        oldest = query_logs(
            session_id=session_id,
            start_ns=start_ns,
            end_ns=end_ns,
            label_filters=label_filters,
            limit=1,
            direction="forward",
            base_url=base_url,
            timeout=timeout,
        )
        newest = query_logs(
            session_id=session_id,
            start_ns=start_ns,
            end_ns=end_ns,
            label_filters=label_filters,
            limit=1,
            direction="backward",
            base_url=base_url,
            timeout=timeout,
        )
        if oldest and newest:
            return (oldest[0]["timestamp_ns"], newest[0]["timestamp_ns"])
    except Exception:
        pass

    records = query_logs(
        session_id=session_id,
        start_ns=start_ns,
        end_ns=end_ns,
        label_filters=label_filters,
        limit=10000,
        base_url=base_url,
        timeout=timeout,
    )
    if not records:
        return None
    timestamps = [r["timestamp_ns"] for r in records]
    return (min(timestamps), max(timestamps))


def delete_logs(
    *,
    session_id: str,
    start_ns: int = 0,
    end_ns: int | None = None,
    base_url: str | None = None,
    timeout: float = 10.0,
) -> None:
    """Submit a delete request for all logs tied to a session id."""
    url = (base_url or config.LOKI_URL).rstrip("/") + LOKI_DELETE_PATH
    params = {
        "query": f'{{session_id="{session_id}"}}',
        "start": str(max(0, start_ns)),
        "end": str(end_ns if end_ns is not None else int(datetime.now(UTC).timestamp() * 1_000_000_000)),
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, params=params)
        resp.raise_for_status()
