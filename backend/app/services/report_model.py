"""Structured incident report: Pydantic model + Markdown renderer.

The agent returns an :class:`IncidentReport` (PydanticAI ``output_type``).
Field validators enforce the section contract — banned conversational
phrases, non-empty steps, etc. The Markdown renderer produces the same shape
the React ``ReportView`` consumes today, so the frontend is unchanged.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

# Section header order — must match render_markdown output exactly.
REPORT_SECTIONS: tuple[str, ...] = (
    "Incident Summary",
    "Possible Root Cause",
    "Uncertainty",
    "Supporting Evidence",
    "Recommended Fix",
    "Next troubleshooting steps",
    "Coding agent fix prompt",
)

_NOT_DETERMINED = "*Not determined.*"

# Phrases that betray a chatty / agentic tone in a read-only report.
# Lowercased substring matches, applied to troubleshooting steps.
_BANNED_OFFER_PHRASES: tuple[str, ...] = (
    "i can run",
    "i'll run",
    "tell me",
    "give me",
    "permission",
    "let me know",
    "would you like",
)


class EvidenceItem(BaseModel):
    """One concrete piece of evidence cited from a tool call."""

    description: str = Field(
        ...,
        description=(
            "What the evidence shows. Cite the underlying source — e.g. "
            "'Loki query for service=payments shows 47 KafkaTimeoutException "
            "errors between 14:02 and 14:08'."
        ),
    )
    source: str = Field(
        ...,
        description="Which tool produced it: one of 'logs', 'metrics', 'docs', 'code'.",
    )


class RecommendedFix(BaseModel):
    """Remediation plan. Non-code actions first; code as last resort."""

    non_code_steps: list[str] = Field(
        default_factory=list,
        description=(
            "Concrete operator actions in priority order: config changes, "
            "restarts, scaling, feature flags. No subheadings, no meta-labels."
        ),
    )
    last_resort_code_change: str | None = Field(
        default=None,
        description=(
            "Optional code-level fix to attempt only after non-code steps are "
            "exhausted. One short paragraph; no implementation details."
        ),
    )


class IncidentReport(BaseModel):
    """Structured incident report. Pydantic-validated; renders to the
    seven-section Markdown contract that the frontend consumes."""

    incident_summary: str = Field(
        ...,
        description="Two-to-four-sentence summary of what happened, scoped to the question.",
    )
    possible_root_cause: str = Field(
        ...,
        description=(
            "Best hypothesis for the underlying cause, anchored in supporting "
            "evidence. Use 'Not determined' only when no causal hypothesis is "
            "supported by the evidence."
        ),
    )
    uncertainty: str = Field(
        ...,
        description=(
            "What is unknown or ambiguous — missing logs, multiple plausible "
            "causes. Use 'Not determined' only when there is no meaningful "
            "uncertainty to state."
        ),
    )
    supporting_evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="Pieces of evidence that ground the root-cause hypothesis.",
    )
    recommended_fix: RecommendedFix = Field(
        default_factory=RecommendedFix,
        description="Remediation plan: non-code first, code as last resort.",
    )
    next_troubleshooting_steps: list[str] = Field(
        default_factory=list,
        description=(
            "Steps a human operator can run to gather more signal "
            "(`kubectl logs`, `docker logs`, env checks, queries to try). "
            "Don't offer to run them yourself; the report is read-only."
        ),
    )
    coding_agent_fix_prompt: str = Field(
        ...,
        description=(
            "Concise implementation prompt for a coding agent. Base it on the "
            "summary + root cause + uncertainty + supporting evidence. Preserve "
            "uncertainty explicitly; do not invent fixes unsupported by evidence."
        ),
    )

    @field_validator("next_troubleshooting_steps")
    @classmethod
    def _no_first_person_offers(cls, v: list[str]) -> list[str]:
        """Reject chatty/agentic phrasing — the report is read-only."""
        for step in v:
            lowered = step.lower()
            for phrase in _BANNED_OFFER_PHRASES:
                if phrase in lowered:
                    raise ValueError(
                        f"step contains banned conversational phrase {phrase!r}: "
                        f"{step!r}. Steps must be operator-runnable, not requests."
                    )
        return v


def render_markdown(report: IncidentReport) -> str:
    """Render an :class:`IncidentReport` to the Markdown shape ``ReportView`` expects.

    Section headers exactly match :data:`REPORT_SECTIONS`. Missing optional
    content falls back to ``*Not determined.*`` so the rendered shape is stable
    even when the agent provides only the required scalars.
    """
    parts: list[str] = []

    parts.append(
        f"## {REPORT_SECTIONS[0]}\n"
        + (report.incident_summary.strip() or _NOT_DETERMINED)
    )
    parts.append(
        f"## {REPORT_SECTIONS[1]}\n"
        + (report.possible_root_cause.strip() or _NOT_DETERMINED)
    )
    parts.append(
        f"## {REPORT_SECTIONS[2]}\n"
        + (report.uncertainty.strip() or _NOT_DETERMINED)
    )

    if report.supporting_evidence:
        evidence_lines = "\n".join(
            f"- ({item.source}) {item.description.strip()}"
            for item in report.supporting_evidence
        )
    else:
        evidence_lines = _NOT_DETERMINED
    parts.append(f"## {REPORT_SECTIONS[3]}\n{evidence_lines}")

    fix_lines: list[str] = []
    for step in report.recommended_fix.non_code_steps:
        text = step.strip()
        if text:
            fix_lines.append(f"- {text}")
    if report.recommended_fix.last_resort_code_change:
        fix_lines.append(
            "- Last resort (code change): "
            + report.recommended_fix.last_resort_code_change.strip()
        )
    parts.append(
        f"## {REPORT_SECTIONS[4]}\n"
        + ("\n".join(fix_lines) if fix_lines else _NOT_DETERMINED)
    )

    if report.next_troubleshooting_steps:
        step_lines = "\n".join(
            f"{i}. {step.strip()}"
            for i, step in enumerate(report.next_troubleshooting_steps, 1)
        )
    else:
        step_lines = _NOT_DETERMINED
    parts.append(f"## {REPORT_SECTIONS[5]}\n{step_lines}")

    parts.append(
        f"## {REPORT_SECTIONS[6]}\n"
        + (report.coding_agent_fix_prompt.strip() or _NOT_DETERMINED)
    )

    return "\n\n".join(parts).strip() + "\n"
