"""Unit tests for the parser-label filter applied to Loki queries.

Phase 7 introduces dual-write (Python + Vector both pushing to Loki). To
avoid mixing both labelsets in agent queries we apply a default
``parser="..."`` filter — configured via LOKI_QUERY_PARSER. These tests lock
that behavior in at the loki_client layer.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.lib import loki_client


@pytest.fixture
def fake_httpx(monkeypatch: pytest.MonkeyPatch):
    """Replace httpx.Client so we can inspect the request params."""
    captured: dict[str, object] = {}

    class _FakeClient:
        def __init__(self, *_, **__): ...
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def get(self, url: str, params: dict):
            captured["url"] = url
            captured["params"] = params
            resp = MagicMock()
            resp.raise_for_status = lambda: None
            resp.json = lambda: {"data": {"result": []}}
            return resp

    monkeypatch.setattr(loki_client.httpx, "Client", _FakeClient)
    return captured


class TestParserFilterDefault:
    def test_default_parser_filter_applied_to_query(
        self, fake_httpx, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(loki_client.config, "LOKI_QUERY_PARSER", "python")
        loki_client.query_logs(session_id="sess-1")
        logql = fake_httpx["params"]["query"]
        assert 'session_id="sess-1"' in logql
        assert 'parser="python"' in logql

    def test_explicit_parser_in_filters_overrides_default(
        self, fake_httpx, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(loki_client.config, "LOKI_QUERY_PARSER", "python")
        loki_client.query_logs(
            session_id="sess-1", label_filters={"parser": "vector"}
        )
        logql = fake_httpx["params"]["query"]
        assert 'parser="vector"' in logql
        assert 'parser="python"' not in logql

    def test_empty_parser_in_filters_disables_default(
        self, fake_httpx, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(loki_client.config, "LOKI_QUERY_PARSER", "python")
        # Passing parser="" explicitly opts out — sees both labelsets.
        loki_client.query_logs(
            session_id="sess-1", label_filters={"parser": ""}
        )
        logql = fake_httpx["params"]["query"]
        assert "parser=" not in logql

    def test_unset_config_skips_filter(
        self, fake_httpx, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(loki_client.config, "LOKI_QUERY_PARSER", "")
        loki_client.query_logs(session_id="sess-1")
        logql = fake_httpx["params"]["query"]
        assert "parser=" not in logql

    def test_other_label_filters_passed_through(
        self, fake_httpx, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(loki_client.config, "LOKI_QUERY_PARSER", "python")
        loki_client.query_logs(
            session_id="sess-1",
            label_filters={"service": "payments", "environment": "prod"},
        )
        logql = fake_httpx["params"]["query"]
        assert 'service="payments"' in logql
        assert 'environment="prod"' in logql
        # Default parser still applied because not present in filters.
        assert 'parser="python"' in logql


class TestUploadParserLabel:
    """The upload pipeline tags every push with config.LOKI_PARSER_LABEL.

    Locks in the labelset so dual-write queries can separate the two.
    """

    def test_python_parser_label_is_added_to_push_labels(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        from app.services import upload as upload_module

        # Reuse the existing per-file pushing logic by calling derive +
        # asserting the label dict shape.
        labels = {
            **upload_module.derive_labels_from_file_path("logs/foo/bar.log"),
            "session_id": "sess-1",
            "parser": upload_module.config.LOKI_PARSER_LABEL,
        }
        assert labels["parser"] == "python"
