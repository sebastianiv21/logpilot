"""Query Prometheus HTTP API for time series (used by agent tools)."""

from __future__ import annotations

import httpx

from app.lib.config import config

PROMETHEUS_QUERY_RANGE = "/api/v1/query_range"
PROMETHEUS_QUERY = "/api/v1/query"

# Metric names we expose (with logpilot_ prefix)
ALLOWED_METRICS = {
    "errors_total",
    "requests_total",
    "error_rate",
    "response_time_seconds",
}
PREFIX = "logpilot_"


def _iso_to_unix_ms(iso_str: str) -> int:
    """Parse ISO 8601 to milliseconds since epoch."""
    from datetime import datetime

    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


def query_range(
    metric_name: str,
    session_id: str,
    start: str,
    end: str,
    *,
    step: str = "15s",
    base_url: str | None = None,
    timeout: float = 10.0,
) -> dict:
    """
    Query Prometheus for a metric in the given time range, scoped to session_id.
    Returns {"values": [[ts_seconds, value], ...], "metric_not_available": bool}.
    """
    # Map user-facing name to our metric name
    if metric_name.startswith(PREFIX):
        prom_metric = metric_name
        normalized = metric_name[len(PREFIX) :]
    else:
        prom_metric = PREFIX + metric_name
        normalized = metric_name
    if normalized not in ALLOWED_METRICS:
        return {
            "values": [],
            "metric_not_available": True,
            "error": f"Unknown metric: {metric_name}",
        }
    url = (base_url or config.PROMETHEUS_URL).rstrip("/") + PROMETHEUS_QUERY_RANGE
    # Prometheus: logpilot_*{session_id="..."}
    query = f'{prom_metric}{{session_id="{session_id}"}}'
    params: dict = {
        "query": query,
        "start": _iso_to_unix_ms(start) / 1000.0,
        "end": _iso_to_unix_ms(end) / 1000.0,
        "step": step,
    }
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
    except Exception as e:
        return {"values": [], "metric_not_available": True, "error": str(e)}
    data = resp.json()
    status = data.get("status")
    if status != "success":
        return {"values": [], "metric_not_available": True, "error": data.get("error", "unknown")}
    result = data.get("data", {}).get("result", [])
    values: list[list[float]] = []
    for series in result:
        for ts_str, value_str in series.get("values", []):
            try:
                ts = float(ts_str)
                val = float(value_str)
                values.append([ts, val])
            except (TypeError, ValueError):
                continue
    values.sort(key=lambda x: x[0])
    return {"values": values, "metric_not_available": len(values) == 0}
