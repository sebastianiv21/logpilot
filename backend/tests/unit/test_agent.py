"""Unit tests for report-generation prompt contracts."""

from app.services.agent import REPORT_SECTIONS, SYSTEM_PROMPT, _ensure_report_sections


def test_report_sections_include_coding_agent_fix_prompt() -> None:
    assert "Coding agent fix prompt" in REPORT_SECTIONS
    assert REPORT_SECTIONS[-1] == "Coding agent fix prompt"


def test_system_prompt_requires_coding_prompt_to_track_evidence_and_uncertainty() -> None:
    assert "Coding agent fix prompt" in SYSTEM_PROMPT
    assert "Possible Root Cause, Uncertainty, and Supporting Evidence" in SYSTEM_PROMPT
    assert "do not invent fixes unsupported by evidence" in SYSTEM_PROMPT


def test_missing_coding_agent_fix_prompt_section_is_appended() -> None:
    content = "## Incident Summary\nShort summary only."

    normalized = _ensure_report_sections(content)

    assert "## Coding agent fix prompt" in normalized
    assert normalized.rstrip().endswith("## Coding agent fix prompt\n*Not determined.*")
