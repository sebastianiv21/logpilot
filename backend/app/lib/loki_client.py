"""Loki push client: POST /loki/api/v1/push with labels and nanosecond timestamps."""
from __future__ import annotations

import httpx

from app.lib.config import config

LOKI_PUSH_PATH = "/loki/api/v1/push"


def _ns_ts(dt_seconds: float) -> str:
    """Convert Unix timestamp (seconds) to nanosecond string for Loki."""
    return str(int(dt_seconds * 1_000_000_000))


def push_logs(
    entries: list[tuple[str, str]],
    labels: dict[str, str],
    *,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> None:
    """
    Push log entries to Loki. Each entry is (timestamp_seconds, log_line).
    Labels are applied to the stream. Timestamps are sent as nanoseconds.
    """
    url = (base_url or config.LOKI_URL).rstrip("/") + LOKI_PUSH_PATH
    values = [[_ns_ts(ts), line] for ts, line in entries]
    payload = {"streams": [{"stream": labels, "values": values}]}
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
