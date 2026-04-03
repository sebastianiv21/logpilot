"""Unit tests for Loki push batching and retry behavior."""

from __future__ import annotations

import httpx

from app.lib import loki_client


class _FakeResponse:
    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text
        self.request = httpx.Request("POST", "http://example.test/loki/api/v1/push")


class _FakeClient:
    def __init__(self, responses: list[_FakeResponse], posted_payloads: list[dict]) -> None:
        self._responses = responses
        self._posted_payloads = posted_payloads

    def __enter__(self) -> _FakeClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def post(self, url: str, json: dict) -> _FakeResponse:
        self._posted_payloads.append({"url": url, "json": json})
        return self._responses.pop(0)


def test_push_logs_splits_large_payloads_into_multiple_batches(monkeypatch) -> None:
    entries = [("1", "a" * 600), ("2", "b" * 600), ("3", "c" * 600)]
    posted_payloads: list[dict] = []
    responses = [_FakeResponse(204), _FakeResponse(204), _FakeResponse(204)]

    monkeypatch.setattr(loki_client.config, "LOKI_URL", "http://example.test")
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_BATCH_BYTES", 1000)
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_RATE_LIMIT_BYTES_PER_SEC", 10_000)
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_MAX_RETRIES", 0)
    monkeypatch.setattr(
        loki_client.httpx,
        "Client",
        lambda timeout: _FakeClient(responses, posted_payloads),
    )
    monkeypatch.setattr(loki_client.time, "sleep", lambda _: None)

    loki_client.push_logs(entries, {"session_id": "abc"})

    assert len(posted_payloads) == 3
    assert posted_payloads[0]["json"]["streams"][0]["values"] == [entries[0]]
    assert posted_payloads[1]["json"]["streams"][0]["values"] == [entries[1]]
    assert posted_payloads[2]["json"]["streams"][0]["values"] == [entries[2]]


def test_push_logs_retries_429_before_succeeding(monkeypatch) -> None:
    entries = [("1", "hello world")]
    posted_payloads: list[dict] = []
    responses = [
        _FakeResponse(429, "rate limited"),
        _FakeResponse(204),
    ]
    sleeps: list[float] = []

    monkeypatch.setattr(loki_client.config, "LOKI_URL", "http://example.test")
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_BATCH_BYTES", 10_000)
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_RATE_LIMIT_BYTES_PER_SEC", 10_000)
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_MAX_RETRIES", 1)
    monkeypatch.setattr(
        loki_client.httpx,
        "Client",
        lambda timeout: _FakeClient(responses, posted_payloads),
    )
    monkeypatch.setattr(loki_client.time, "sleep", lambda seconds: sleeps.append(seconds))

    loki_client.push_logs(entries, {"session_id": "abc"})

    assert len(posted_payloads) == 2
    assert sleeps[0] == 1


def test_push_logs_raises_after_exhausting_retries(monkeypatch) -> None:
    entries = [("1", "hello world")]
    posted_payloads: list[dict] = []
    responses = [
        _FakeResponse(429, "rate limited"),
        _FakeResponse(429, "still rate limited"),
    ]

    monkeypatch.setattr(loki_client.config, "LOKI_URL", "http://example.test")
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_BATCH_BYTES", 10_000)
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_RATE_LIMIT_BYTES_PER_SEC", 10_000)
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_MAX_RETRIES", 1)
    monkeypatch.setattr(
        loki_client.httpx,
        "Client",
        lambda timeout: _FakeClient(responses, posted_payloads),
    )
    monkeypatch.setattr(loki_client.time, "sleep", lambda _: None)

    try:
        loki_client.push_logs(entries, {"session_id": "abc"})
    except httpx.HTTPStatusError as exc:
        assert "Loki push failed (429)" in str(exc)
    else:
        raise AssertionError("Expected HTTPStatusError")

    assert len(posted_payloads) == 2


def test_push_logs_splits_oversized_single_entry(monkeypatch) -> None:
    entries = [("1", "x" * 1200)]
    posted_payloads: list[dict] = []
    responses = [_FakeResponse(204), _FakeResponse(204)]

    monkeypatch.setattr(loki_client.config, "LOKI_URL", "http://example.test")
    monkeypatch.setattr(loki_client.config, "LOKI_MAX_ENTRY_BYTES", 700)
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_BATCH_BYTES", 10_000)
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_RATE_LIMIT_BYTES_PER_SEC", 10_000)
    monkeypatch.setattr(loki_client.config, "LOKI_PUSH_MAX_RETRIES", 0)
    monkeypatch.setattr(
        loki_client.httpx,
        "Client",
        lambda timeout: _FakeClient(responses, posted_payloads),
    )
    monkeypatch.setattr(loki_client.time, "sleep", lambda _: None)

    loki_client.push_logs(entries, {"session_id": "abc"})

    values = posted_payloads[0]["json"]["streams"][0]["values"]
    assert len(values) == 2
    assert values[0][0] == "1"
    assert values[1][0] == "1"
    assert values[0][1].endswith(loki_client.ENTRY_SPLIT_SUFFIX)
    assert len(values[0][1].encode("utf-8")) + loki_client.ENTRY_OVERHEAD_BYTES <= 700
    assert len(values[1][1].encode("utf-8")) + loki_client.ENTRY_OVERHEAD_BYTES <= 700
