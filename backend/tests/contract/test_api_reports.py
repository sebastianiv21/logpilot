"""Contract tests for reports API and report metadata surfaces."""

from __future__ import annotations

import re

import pytest
from app.api import reports as reports_api
from app.api.app import app
from app.lib import config as app_config
from app.lib.repositories import ReportRepository
from app.services.export import PDFExportRenderError, PDFExportStats, PDFExportTooLargeError
from fastapi.testclient import TestClient

QUESTION = "Why did checkout requests start timing out after the deploy?"
REPORT_CONTENT = (
    "## Incident Summary\n"
    "Checkout requests started timing out after the deploy.\n\n"
    "## Possible Root Cause\n"
    "The new release likely introduced a slow downstream call.\n\n"
    "## Uncertainty\n"
    "Need more data on whether retries amplified latency.\n\n"
    "## Supporting Evidence\n"
    "- Error rate increased after deploy\n"
    "- Retry counts increased from `1` to `5`\n\n"
    "```python\n"
    "def load_inventory(tenant_id: str) -> None:\n"
    "    if tenant_id in rollout_enabled_tenants:\n"
    '        raise TimeoutError("inventory call exceeded 30s")\n'
    "```\n\n"
    "## Recommended Fix\n"
    "- Roll back or gate the slow code path\n\n"
    "## Coding agent fix prompt\n"
    "Update the request path to avoid the slow downstream call while preserving "
    "uncertainty about retry amplification.\n\n"
    "## Next troubleshooting steps\n"
    "1. Compare latency before and after deploy.\n"
    "2. Inspect retry behavior for the downstream dependency.\n"
)
TOO_LARGE_DETAIL = (
    "PDF export is unavailable for this report. Use Markdown export instead."
)


def _session_id(client: TestClient) -> str:
    response = client.post("/sessions", json={"name": "report-test"})
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture
def client(monkeypatch) -> TestClient:
    monkeypatch.setattr(app_config.config, "LLM_API_KEY", "test-key")
    return TestClient(app)


def _create_report(session_id: str):
    return ReportRepository().create(
        session_id=session_id,
        content=REPORT_CONTENT,
        question=QUESTION,
    )


def _fake_generate_incident_report(
    session_id: str,
    question: str,
    *,
    report_id: str | None = None,
):
    repo = ReportRepository()
    content = REPORT_CONTENT.replace("after the deploy", question)
    if report_id is not None:
        updated = repo.update_content(report_id, session_id, content)
        assert updated
        return {"report_id": report_id, "content": content}
    created = repo.create(session_id=session_id, content=content, question=question)
    return {"report_id": created.id, "content": content}


def test_generate_report_persists_question_and_detail_shape(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
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
    ReportRepository().create(
        session_id=session_id,
        content=REPORT_CONTENT,
        question=long_question,
    )

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
    report = _create_report(session_id)

    response = client.get(f"/sessions/{session_id}/reports/{report.id}/export?format=markdown")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "## Coding agent fix prompt" in response.text
    assert re.search(r"^1\. ", response.text, re.M)


def test_export_pdf_streams_pdf_response(client: TestClient) -> None:
    session_id = _session_id(client)
    report = _create_report(session_id)

    response = client.get(f"/sessions/{session_id}/reports/{report.id}/export?format=pdf")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.content.startswith(b"%PDF")


def test_export_pdf_returns_deterministic_error_on_renderer_failure(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _session_id(client)
    report = _create_report(session_id)

    def _boom(_: str):
        raise PDFExportRenderError(
            PDFExportStats(
                report_chars=len(REPORT_CONTENT),
                code_fence_count=1,
                code_block_line_count=4,
                block_count=6,
                flowable_count=12,
            )
        )

    monkeypatch.setattr(reports_api, "export_pdf_to_file", _boom)

    response = client.get(f"/sessions/{session_id}/reports/{report.id}/export?format=pdf")

    assert response.status_code == 503
    assert response.json()["detail"] == reports_api.PDF_EXPORT_FAILURE_DETAIL


def test_export_pdf_returns_deterministic_error_on_guardrail_rejection(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id = _session_id(client)
    report = _create_report(session_id)
    stats = PDFExportStats(
        report_chars=500_000,
        code_fence_count=1,
        code_block_line_count=5_000,
        block_count=3_000,
    )

    def _reject(_: str):
        raise PDFExportTooLargeError(TOO_LARGE_DETAIL, stats)

    monkeypatch.setattr(reports_api, "export_pdf_to_file", _reject)

    response = client.get(f"/sessions/{session_id}/reports/{report.id}/export?format=pdf")

    assert response.status_code == 413
    assert response.json()["detail"] == TOO_LARGE_DETAIL
