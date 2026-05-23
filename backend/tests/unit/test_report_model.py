"""Unit tests for the IncidentReport pydantic model and render_markdown."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.services.report_model import (
    REPORT_SECTIONS,
    EvidenceItem,
    IncidentReport,
    RecommendedFix,
    render_markdown,
)


def _minimal_report(**overrides) -> IncidentReport:
    base = dict(
        incident_summary="Payments service started returning 503s at 14:02.",
        possible_root_cause="Kafka cluster lost quorum, blocking publish.",
        uncertainty="Not determined.",
        coding_agent_fix_prompt="Investigate Kafka quorum loss in payments.",
    )
    base.update(overrides)
    return IncidentReport(**base)


class TestRequiredFields:
    def test_minimal_report_validates(self) -> None:
        _minimal_report()  # does not raise

    @pytest.mark.parametrize(
        "missing",
        [
            "incident_summary",
            "possible_root_cause",
            "uncertainty",
            "coding_agent_fix_prompt",
        ],
    )
    def test_required_scalar_fields(self, missing: str) -> None:
        payload = dict(
            incident_summary="x",
            possible_root_cause="y",
            uncertainty="z",
            coding_agent_fix_prompt="w",
        )
        payload.pop(missing)
        with pytest.raises(ValidationError):
            IncidentReport(**payload)

    def test_list_and_nested_fields_default_to_empty(self) -> None:
        report = _minimal_report()
        assert report.supporting_evidence == []
        assert report.next_troubleshooting_steps == []
        assert isinstance(report.recommended_fix, RecommendedFix)
        assert report.recommended_fix.non_code_steps == []
        assert report.recommended_fix.last_resort_code_change is None


class TestBannedPhrasesValidator:
    @pytest.mark.parametrize(
        "step",
        [
            "I can run kubectl logs against the pod",
            "Tell me the service name",
            "Give me permission to query the database",
            "I'll run a quick check",
            "Let me know if you want me to dig deeper",
            "Would you like me to investigate further",
        ],
    )
    def test_first_person_offers_rejected(self, step: str) -> None:
        with pytest.raises(ValidationError, match="banned conversational phrase"):
            _minimal_report(next_troubleshooting_steps=[step])

    def test_legitimate_operator_step_accepted(self) -> None:
        _minimal_report(
            next_troubleshooting_steps=[
                "Run `kubectl logs payments-7b9c -n prod --tail=200` and grep for KafkaTimeoutException.",
                "Run `docker logs payments` if running outside Kubernetes.",
            ]
        )


class TestMarkdownRenderer:
    def test_renders_every_section_in_order(self) -> None:
        report = _minimal_report(
            supporting_evidence=[
                EvidenceItem(description="Loki shows 47 errors in 6 minutes.", source="logs"),
            ],
            recommended_fix=RecommendedFix(
                non_code_steps=["Restart payments deployment."],
                last_resort_code_change="Add retry with exponential backoff to producer.",
            ),
            next_troubleshooting_steps=["Run `kubectl describe pod payments-7b9c`."],
        )
        out = render_markdown(report)
        # Every section header present, in order
        last = -1
        for section in REPORT_SECTIONS:
            idx = out.find(f"## {section}")
            assert idx > last, f"section out of order or missing: {section}"
            last = idx

    def test_missing_optional_fields_render_not_determined(self) -> None:
        out = render_markdown(_minimal_report())
        assert "## Supporting Evidence\n*Not determined.*" in out
        assert "## Recommended Fix\n*Not determined.*" in out
        assert "## Next troubleshooting steps\n*Not determined.*" in out

    def test_evidence_items_render_with_source_tag(self) -> None:
        report = _minimal_report(
            supporting_evidence=[
                EvidenceItem(description="Error count spiked 50x.", source="metrics"),
                EvidenceItem(description="Stack trace shows quorum loss.", source="logs"),
            ],
        )
        out = render_markdown(report)
        assert "- (metrics) Error count spiked 50x." in out
        assert "- (logs) Stack trace shows quorum loss." in out

    def test_last_resort_code_change_prefixed_correctly(self) -> None:
        report = _minimal_report(
            recommended_fix=RecommendedFix(
                non_code_steps=["Scale payments to 5 replicas."],
                last_resort_code_change="Add circuit breaker.",
            ),
        )
        out = render_markdown(report)
        assert "- Scale payments to 5 replicas." in out
        assert "- Last resort (code change): Add circuit breaker." in out

    def test_troubleshooting_steps_render_as_numbered_list(self) -> None:
        report = _minimal_report(
            next_troubleshooting_steps=[
                "First step.",
                "Second step.",
                "Third step.",
            ],
        )
        out = render_markdown(report)
        assert "1. First step." in out
        assert "2. Second step." in out
        assert "3. Third step." in out

    def test_output_ends_with_single_trailing_newline(self) -> None:
        out = render_markdown(_minimal_report())
        assert out.endswith("\n")
        assert not out.endswith("\n\n")
