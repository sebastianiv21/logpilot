"""Unit tests for agent prompt contracts and the public surface.

We don't exercise the LLM here — that's covered by integration tests with a
real model. These checks lock in the instruction text (regression guard) and
verify ``generate_incident_report`` wires the structured output into the
repository correctly.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.services.agent import (
    AGENT_INSTRUCTIONS,
    REPORT_SECTIONS,
    SYSTEM_PROMPT,
    AgentDeps,
    generate_incident_report,
)
from app.services.report_model import IncidentReport, RecommendedFix


# ---------------------------------------------------------------------------
# Prompt-content guards (catch accidental deletions of key guidance)
# ---------------------------------------------------------------------------


def test_system_prompt_is_alias_of_instructions() -> None:
    assert SYSTEM_PROMPT == AGENT_INSTRUCTIONS


def test_report_sections_end_with_coding_agent_fix_prompt() -> None:
    assert "Coding agent fix prompt" in REPORT_SECTIONS
    assert REPORT_SECTIONS[-1] == "Coding agent fix prompt"


@pytest.mark.parametrize(
    "fragment",
    [
        "Read-only tools",
        "Cite evidence",
        "do not invent fixes",  # may wrap across a line in the source
        "Preserve uncertainty explicitly",
        "next_troubleshooting_steps",
        "recommended_fix.non_code_steps",
        "recommended_fix.last_resort_code_change",
        "coding_agent_fix_prompt",
    ],
)
def test_instructions_retain_key_guidance(fragment: str) -> None:
    assert fragment in AGENT_INSTRUCTIONS


# ---------------------------------------------------------------------------
# generate_incident_report wiring
# ---------------------------------------------------------------------------


def _fake_report() -> IncidentReport:
    return IncidentReport(
        incident_summary="Payments 503 spike at 14:02.",
        possible_root_cause="Kafka quorum loss.",
        uncertainty="Not determined.",
        recommended_fix=RecommendedFix(non_code_steps=["Restart payments."]),
        next_troubleshooting_steps=["Run `kubectl logs payments`."],
        coding_agent_fix_prompt="Investigate Kafka client retry behavior.",
    )


def test_generate_incident_report_creates_new_when_no_report_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import agent as agent_module

    monkeypatch.setattr(agent_module.config, "LLM_API_KEY", "test-key")

    fake_run_result = MagicMock()
    fake_run_result.output = _fake_report()
    fake_agent = MagicMock()
    fake_agent.run_sync.return_value = fake_run_result

    with patch.object(agent_module, "_make_agent", return_value=fake_agent) as make_agent, \
         patch.object(agent_module, "ReportRepository") as MockRepo:
        created = MagicMock()
        created.id = "rep-123"
        created.content = "rendered markdown"
        MockRepo.return_value.create.return_value = created

        result = generate_incident_report("sess-1", "Why are payments 503ing?")

    make_agent.assert_called_once()
    fake_agent.run_sync.assert_called_once()
    # Deps must be threaded through with the session id
    _, kwargs = fake_agent.run_sync.call_args
    assert isinstance(kwargs["deps"], AgentDeps)
    assert kwargs["deps"].session_id == "sess-1"
    assert result == {"report_id": "rep-123", "content": "rendered markdown"}


def test_generate_incident_report_updates_existing_when_report_id_given(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import agent as agent_module

    monkeypatch.setattr(agent_module.config, "LLM_API_KEY", "test-key")

    fake_run_result = MagicMock()
    fake_run_result.output = _fake_report()
    fake_agent = MagicMock()
    fake_agent.run_sync.return_value = fake_run_result

    with patch.object(agent_module, "_make_agent", return_value=fake_agent), \
         patch.object(agent_module, "ReportRepository") as MockRepo:
        MockRepo.return_value.update_content.return_value = True

        result = generate_incident_report(
            "sess-1", "Why are payments 503ing?", report_id="rep-existing"
        )

    MockRepo.return_value.update_content.assert_called_once()
    args = MockRepo.return_value.update_content.call_args.args
    assert args[0] == "rep-existing"
    assert args[1] == "sess-1"
    # Third arg is the rendered markdown — must include every section header.
    rendered: str = args[2]
    for section in REPORT_SECTIONS:
        assert f"## {section}" in rendered
    assert result["report_id"] == "rep-existing"


def test_generate_incident_report_raises_when_update_target_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import agent as agent_module

    monkeypatch.setattr(agent_module.config, "LLM_API_KEY", "test-key")

    fake_run_result = MagicMock()
    fake_run_result.output = _fake_report()
    fake_agent = MagicMock()
    fake_agent.run_sync.return_value = fake_run_result

    with patch.object(agent_module, "_make_agent", return_value=fake_agent), \
         patch.object(agent_module, "ReportRepository") as MockRepo:
        MockRepo.return_value.update_content.return_value = False

        with pytest.raises(ValueError, match="Report not found"):
            generate_incident_report(
                "sess-1", "Why?", report_id="rep-missing"
            )


def test_generate_incident_report_requires_llm_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import agent as agent_module

    monkeypatch.setattr(agent_module.config, "LLM_API_KEY", "")
    with pytest.raises(ValueError, match="LLM_API_KEY not set"):
        generate_incident_report("sess-1", "Why?")
