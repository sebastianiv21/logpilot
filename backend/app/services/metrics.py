"""Derive metrics from parsed log events: errors, requests, error rate, response time."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.services.log_parser import ParsedLogRecord

ERROR_LEVELS = frozenset({"ERROR", "FATAL"})

LATENCY_KEYS = ("duration", "latency", "response_time", "elapsed", "time_ms", "took", "dur")

_LATENCY_RE = re.compile(
    r"(?:in|took|duration|latency|elapsed|response.?time)[=:\s]*"
    r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>ms|s|seconds|milliseconds)?",
    re.IGNORECASE,
)

_BARE_MS_RE = re.compile(r"\b(?P<value>\d+(?:\.\d+)?)(?P<unit>ms)\b")


@dataclass
class DerivedMetrics:
    """Aggregated metrics from a batch of log records."""

    errors_total: int
    requests_total: int
    error_rate: float
    response_times: list[float]  # seconds


def _extract_latency_from_json(raw: str) -> float | None:
    """Try to parse raw_message as JSON and extract a latency value in seconds."""
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError, TypeError:
        return None
    if not isinstance(obj, dict):
        return None
    for key in LATENCY_KEYS:
        val = obj.get(key)
        if val is None:
            continue
        try:
            num = float(val)
        except TypeError, ValueError:
            continue
        if num < 0:
            continue
        if key in ("time_ms", "dur") or "ms" in key.lower():
            return num / 1000.0
        if num > 1000:
            return num / 1000.0
        return num
    return None


def _extract_latency_from_text(message: str) -> float | None:
    """Extract latency from unstructured text via regex."""
    for pattern in (_LATENCY_RE, _BARE_MS_RE):
        m = pattern.search(message)
        if m:
            value = float(m.group("value"))
            unit = (m.group("unit") or "ms").lower()
            if unit in ("ms", "milliseconds"):
                return value / 1000.0
            return value
    return None


def extract_latency(record: ParsedLogRecord) -> float | None:
    """Attempt to extract a response time (in seconds) from a log record."""
    lat = _extract_latency_from_json(record.raw_message)
    if lat is not None:
        return lat
    return _extract_latency_from_text(record.message)


def derive_metrics(records: list[ParsedLogRecord]) -> DerivedMetrics:
    """
    Compute aggregate metrics from a batch of parsed log records.

    Returns a DerivedMetrics with error/request counts, error rate,
    and a list of extracted response times (seconds).
    """
    errors = 0
    total = len(records)
    response_times: list[float] = []

    for record in records:
        if record.log_level in ERROR_LEVELS:
            errors += 1

        lat = extract_latency(record)
        if lat is not None:
            response_times.append(lat)

    error_rate = (errors / total) if total > 0 else 0.0

    return DerivedMetrics(
        errors_total=errors,
        requests_total=total,
        error_rate=error_rate,
        response_times=response_times,
    )
