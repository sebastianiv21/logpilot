"""Prometheus metrics registry and instrumentation for LogPilot."""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

registry = CollectorRegistry()

errors_total = Counter(
    "logpilot_errors_total",
    "Total error-level log lines ingested",
    ["session_id", "service"],
    registry=registry,
)

requests_total = Counter(
    "logpilot_requests_total",
    "Total log lines ingested (proxy for request volume)",
    ["session_id", "service"],
    registry=registry,
)

error_rate = Gauge(
    "logpilot_error_rate",
    "Error rate (errors / total) per session and service",
    ["session_id", "service"],
    registry=registry,
)

response_time_seconds = Histogram(
    "logpilot_response_time_seconds",
    "Response time distribution extracted from log lines",
    ["session_id", "service"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry,
)


def record_metrics(
    *,
    session_id: str,
    service: str,
    errors: int,
    total: int,
    rate: float,
    response_times: list[float],
) -> None:
    """Push derived metric values into the Prometheus collectors."""
    labels = {"session_id": session_id, "service": service}
    errors_total.labels(**labels).inc(errors)
    requests_total.labels(**labels).inc(total)
    error_rate.labels(**labels).set(rate)
    hist = response_time_seconds.labels(**labels)
    for t in response_times:
        hist.observe(t)


def get_metrics() -> bytes:
    """Return Prometheus metrics in text exposition format."""
    return generate_latest(registry)
