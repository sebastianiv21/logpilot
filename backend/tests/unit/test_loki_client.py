"""Unit tests for Loki delete behavior."""

from __future__ import annotations

import httpx

from app.lib import loki_client


class _FakeResponse:
    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text
        self.request = httpx.Request("POST", "http://example.test/loki/api/v1/delete")

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"{self.status_code}", request=self.request, response=self  # type: ignore[arg-type]
            )


class _FakeClient:
    def __init__(self, responses: list[_FakeResponse], posted_payloads: list[dict]) -> None:
        self._responses = responses
        self._posted_payloads = posted_payloads

    def __enter__(self) -> "_FakeClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def post(self, url: str, params: dict) -> _FakeResponse:
        self._posted_payloads.append({"url": url, "params": params})
        return self._responses.pop(0)


def test_delete_logs_posts_delete_request_for_session_selector(monkeypatch) -> None:
    posted_payloads: list[dict] = []
    responses = [_FakeResponse(204)]

    monkeypatch.setattr(loki_client.config, "LOKI_URL", "http://example.test")
    monkeypatch.setattr(
        loki_client.httpx,
        "Client",
        lambda timeout: _FakeClient(responses, posted_payloads),
    )

    loki_client.delete_logs(session_id="abc", start_ns=10, end_ns=20)

    assert posted_payloads == [
        {
            "url": "http://example.test/loki/api/v1/delete",
            "params": {
                "query": '{session_id="abc"}',
                "start": "10",
                "end": "20",
            },
        }
    ]
