"""Contract tests for reports API and report metadata surfaces."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from app.api import reports as reports_api
from app.api.app import app
from app.lib import config as app_config
from app.lib.repositories import ReportRepository

QUESTION = "Why did checkout requests start timing out after the deploy?"
REPORT_CONTENT = """## Incident Summary
Checkout requests started timing out after the deploy.

## Possible Root Cause
The new release likely introduced a slow downstream call.

## Uncertainty
Need more data on whether retries amplified latency.

## Supporting Evidence
- Error rate increased after deploy

## Recommended Fix
- Roll back or gate the slow code path

## Coding agent fix prompt
Update the request path to avoid the slow downstream call, and preserve uncertainty about retry amplification in comments and tests.

## Next troubleshooting steps
1. Compare latency before and after deploy.
2. Inspect retry behavior for the downstream dependency.
"""


def _session_id(client: TestClient) -> str:
    response = client.post("/sessions", json={"name": "report-test"})
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setattr(app_config.config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(app_config.config, "LLM_API_KEY", "test-key")
    return TestClient(app)


def _fake_generate_incident_report(session_id: str, question: str, *, report_id: str | None = None):
    repo = ReportRepository()
    content = REPORT_CONTENT.replace("after the deploy", question)
    if report_id is not None:
        updated = repo.update_content(report_id, session_id, content)
        assert updated
        return {"report_id": report_id, "content": content}
    created = repo.create(session_id=session_id, content=content, question=question)
    return {"report_id": created.id, "content": content}


def test_generate_report_persists_question_and_detail_shape(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(reports_api, "generate_incident_report", _fake_generate_incident_report)
    session_id = _session_id(client)

    response = client.post(
        f"/sessions/{session_id}/reports/generate",
        json={"question": QUESTION},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["session_id"] == session_id
    assert data["content"] is None

    report_id = data["id"]
    detail = client.get(f"/sessions/{session_id}/reports/{report_id}")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["question"] == QUESTION
    assert "## Coding agent fix prompt" in payload["content"]
    assert "## Next troubleshooting steps" in payload["content"]


def test_report_list_includes_preview_and_has_question_flag(client: TestClient) -> None:
    session_id = _session_id(client)
    repo = ReportRepository()
    repo.create(session_id=session_id, content=REPORT_CONTENT, question=QUESTION)
    repo.create(session_id=session_id, content="legacy content", question=None)

    response = client.get(f"/sessions/{session_id}/reports")

    assert response.status_code == 200
    reports = response.json()["reports"]
    assert len(reports) == 2
    with_question = next(item for item in reports if item["has_question"] is True)
    without_question = next(item for item in reports if item["has_question"] is False)
    assert with_question["question_preview"] == QUESTION
    assert without_question["question_preview"] is None


def test_report_list_preview_is_truncated_for_long_questions(client: TestClient) -> None:
    session_id = _session_id(client)
    long_question = " ".join(["timeout"] * 40)
    ReportRepository().create(session_id=session_id, content=REPORT_CONTENT, question=long_question)

    response = client.get(f"/sessions/{session_id}/reports")

    assert response.status_code == 200
    preview = response.json()["reports"][0]["question_preview"]
    assert preview.endswith("…")
    assert len(preview) <= 96


def test_generate_report_rejects_blank_question(client: TestClient) -> None:
    session_id = _session_id(client)

    response = client.post(
        f"/sessions/{session_id}/reports/generate",
        json={"question": "   "},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Incident question cannot be empty"


def test_export_markdown_preserves_coding_agent_fix_prompt(client: TestClient) -> None:
    session_id = _session_id(client)
    report = ReportRepository().create(session_id=session_id, content=REPORT_CONTENT, question=QUESTION)

    response = client.get(f"/sessions/{session_id}/reports/{report.id}/export?format=markdown")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "## Coding agent fix prompt" in response.text
    assert re.search(r"^1\. ", response.text, re.M)
