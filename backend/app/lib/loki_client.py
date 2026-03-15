"""Loki push and query client: push with labels/nanosecond timestamps; query_range for logs."""

from __future__ import annotations

import httpx

from app.lib.config import config

LOKI_PUSH_PATH = "/loki/api/v1/push"
LOKI_QUERY_RANGE_PATH = "/loki/api/v1/query_range"


def push_logs(
    entries: list[tuple[str, str]],
    labels: dict[str, str],
    *,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> None:
    """
    Push log entries to Loki. Each entry is (timestamp_ns_string, log_line).
    Labels are applied to the stream.
    """
    url = (base_url or config.LOKI_URL).rstrip("/") + LOKI_PUSH_PATH
    payload = {"streams": [{"stream": labels, "values": entries}]}
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=payload)
        if resp.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"Loki push failed ({resp.status_code}): {resp.text}",
                request=resp.request,
                response=resp,
            )


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
    # Build LogQL: {session_id="..." [, label=value, ...] }
    parts = [f'session_id="{session_id}"']
    if label_filters:
        for k, v in label_filters.items():
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
    import time

    end_ns = int(time.time() * 1_000_000_000)
    start_ns = 0  # epoch; covers all logs

    try:
        # Oldest log: direction=forward, limit=1
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
        # Newest log: direction=backward, limit=1
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
        pass  # fallback below

    # Fallback: single query with wide range and large limit (no direction)
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
