"""Loki push and query client: push with labels/nanosecond timestamps; query_range for logs."""

from __future__ import annotations

import time
from datetime import UTC, datetime

import httpx

from app.lib.config import config

LOKI_PUSH_PATH = "/loki/api/v1/push"
LOKI_QUERY_RANGE_PATH = "/loki/api/v1/query_range"
LOKI_DELETE_PATH = "/loki/api/v1/delete"
ENTRY_OVERHEAD_BYTES = 128
ENTRY_SPLIT_SUFFIX = "\n[logpilot split]"


def _estimate_entry_bytes(entry: tuple[str, str]) -> int:
    """Estimate serialized size with safety margin for JSON framing."""
    timestamp_ns, line = entry
    return len(timestamp_ns) + len(line.encode("utf-8")) + ENTRY_OVERHEAD_BYTES


def _split_oversized_entries(
    entries: list[tuple[str, str]],
    *,
    max_entry_bytes: int,
) -> list[tuple[str, str]]:
    """Split oversized Loki entries into smaller UTF-8 safe chunks."""
    if max_entry_bytes <= ENTRY_OVERHEAD_BYTES:
        return entries

    split_entries: list[tuple[str, str]] = []
    max_line_bytes = max_entry_bytes - ENTRY_OVERHEAD_BYTES
    suffix_bytes = len(ENTRY_SPLIT_SUFFIX.encode("utf-8"))

    for timestamp_ns, line in entries:
        line_bytes = line.encode("utf-8")
        if len(line_bytes) <= max_line_bytes:
            split_entries.append((timestamp_ns, line))
            continue

        chunk_budget = max(1, max_line_bytes - suffix_bytes)
        start = 0
        while start < len(line_bytes):
            end = min(start + chunk_budget, len(line_bytes))
            while end < len(line_bytes) and (line_bytes[end] & 0b1100_0000) == 0b1000_0000:
                end -= 1
            if end <= start:
                end = min(start + chunk_budget, len(line_bytes))
            chunk = line_bytes[start:end].decode("utf-8", errors="ignore")
            if end < len(line_bytes):
                chunk += ENTRY_SPLIT_SUFFIX
            split_entries.append((timestamp_ns, chunk))
            start = end

    return split_entries


def _chunk_entries(
    entries: list[tuple[str, str]],
    *,
    max_batch_bytes: int,
) -> list[list[tuple[str, str]]]:
    """Split entries into size-bounded batches while preserving order."""
    if not entries:
        return []
    if max_batch_bytes <= 0:
        return [entries]

    batches: list[list[tuple[str, str]]] = []
    current_batch: list[tuple[str, str]] = []
    current_bytes = 0

    for entry in entries:
        entry_bytes = _estimate_entry_bytes(entry)
        if current_batch and current_bytes + entry_bytes > max_batch_bytes:
            batches.append(current_batch)
            current_batch = []
            current_bytes = 0
        current_batch.append(entry)
        current_bytes += entry_bytes

    if current_batch:
        batches.append(current_batch)
    return batches


def _push_batch(
    client: httpx.Client,
    url: str,
    labels: dict[str, str],
    entries: list[tuple[str, str]],
    *,
    max_retries: int,
) -> None:
    """Push one batch to Loki and retry briefly on 429 responses."""
    payload = {"streams": [{"stream": labels, "values": entries}]}
    for attempt in range(max_retries + 1):
        resp = client.post(url, json=payload)
        if resp.status_code < 400:
            return
        if resp.status_code == 429 and attempt < max_retries:
            time.sleep(min(2**attempt, 4))
            continue
        raise httpx.HTTPStatusError(
            f"Loki push failed ({resp.status_code}): {resp.text}",
            request=resp.request,
            response=resp,
        )


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
    if not entries:
        return

    url = (base_url or config.LOKI_URL).rstrip("/") + LOKI_PUSH_PATH
    entries = _split_oversized_entries(
        entries,
        max_entry_bytes=max(1, config.LOKI_MAX_ENTRY_BYTES),
    )
    max_batch_bytes = max(1, config.LOKI_PUSH_BATCH_BYTES)
    max_rate_bytes_per_sec = max(0, config.LOKI_PUSH_RATE_LIMIT_BYTES_PER_SEC)
    max_retries = max(0, config.LOKI_PUSH_MAX_RETRIES)
    batches = _chunk_entries(entries, max_batch_bytes=max_batch_bytes)

    with httpx.Client(timeout=timeout) as client:
        for index, batch in enumerate(batches):
            _push_batch(client, url, labels, batch, max_retries=max_retries)
            if max_rate_bytes_per_sec > 0 and index < len(batches) - 1:
                batch_bytes = sum(_estimate_entry_bytes(entry) for entry in batch)
                time.sleep(batch_bytes / max_rate_bytes_per_sec)


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
