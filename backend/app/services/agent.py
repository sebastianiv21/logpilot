"""AI agent: PydanticAI runtime producing a structured IncidentReport.

Replaces the hand-rolled OpenAI tool loop. The agent's response is a
:class:`IncidentReport` validated by Pydantic; missing sections, banned
phrasing, and missing fields are caught structurally — no post-hoc patching.

Public surface (unchanged for callers):
    generate_incident_report(session_id, question, *, report_id=None)
        -> {"report_id": str, "content": str}
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.lib.config import config
from app.lib.repositories import ReportRepository
from app.services import agent_tools, incident_memory
from app.services.incident_memory import PastIncident
from app.services.report_model import REPORT_SECTIONS, IncidentReport, render_markdown

logger = logging.getLogger(__name__)


AGENT_INSTRUCTIONS = """You are an incident investigation assistant. Read-only tools:
- query_logs: log store (query, start, end, limit)
- search_docs: semantic search over docs/knowledge
- search_past_incidents: find prior incident reports semantically similar to a
  query. Call this early when the symptoms are concrete (specific error
  strings, services, root-cause families) — it's how you check "have we seen
  this before?" before proposing a fix. Excludes the current session.
- grep_repo: literal/regex search over source code (ripgrep). Use this when you
  have a concrete token to look up — error strings, function names from stack
  traces, service identifiers, file paths. Prefer narrow patterns and globs.
- read_file: read a bounded slice of a source file by path + line range. Chain
  after grep_repo to see surrounding implementation.

Gather evidence via tools, then return a structured IncidentReport.

Guidance for each section:
- recommended_fix.non_code_steps: List concrete operator actions only, in priority
  order. No subheadings, no meta-labels (e.g. don't write "Non-code actions (do
  these first)", "Immediate actions", "Prefer non-code actions").
- recommended_fix.last_resort_code_change: Use only when non-code remediation is
  insufficient. One short paragraph; no implementation details.
- next_troubleshooting_steps: Steps a human operator can run (`kubectl logs`,
  `docker logs`, env checks, queries to try). Don't assume only Kubernetes —
  include Docker variants when relevant. Don't say "I can run...", "tell me...",
  or "give me permission..." — the report is read-only.
- coding_agent_fix_prompt: Concise implementation prompt for a coding agent.
  Base it on incident_summary + possible_root_cause + uncertainty +
  supporting_evidence. Preserve uncertainty explicitly; do not invent fixes
  unsupported by evidence.
- uncertainty: What's unknown or ambiguous given the evidence. Use "Not
  determined" only when there is no meaningful uncertainty to state.
- related_past_incidents: When search_past_incidents returns matches, keep
  only the ones that are genuinely relevant — same symptoms, same service,
  same root-cause family. For each kept match, write a short why_relevant
  explaining the link. Leave empty when no prior incident is similar enough
  to warrant surfacing; do not pad.
- Formatting: wrap file paths, env var names, short error strings, and inline
  code in single backticks. Use fenced code blocks for multi-line snippets.
- Cite evidence in supporting_evidence."""


@dataclass
class AgentDeps:
    """Per-run context passed to every session-scoped tool."""

    session_id: str


def _build_model() -> OpenAIChatModel:
    """Configure PydanticAI's OpenAI-compatible adapter from app config."""
    if not config.LLM_API_KEY:
        raise ValueError("LLM_API_KEY not set")
    return OpenAIChatModel(
        config.LLM_MODEL,
        provider=OpenAIProvider(
            base_url=config.LLM_BASE_URL or "https://api.openai.com/v1",
            api_key=config.LLM_API_KEY,
        ),
    )


def _make_agent() -> Agent[AgentDeps, IncidentReport]:
    """Build the agent and register tools. Built per-call so config changes
    (e.g. a swapped LLM_API_KEY) take effect without a process restart."""
    agent: Agent[AgentDeps, IncidentReport] = Agent(
        _build_model(),
        output_type=IncidentReport,
        deps_type=AgentDeps,
        instructions=AGENT_INSTRUCTIONS,
        model_settings={"temperature": 0.2},
    )

    @agent.tool
    def query_logs(
        ctx: RunContext[AgentDeps],
        query: str = "",
        start: str | None = None,
        end: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Query the session's log store. Returns entries with timestamp,
        level, service, raw_message. start/end ISO 8601; limit capped at 1000."""
        return agent_tools.query_logs(
            session_id=ctx.deps.session_id,
            query=query,
            start=start,
            end=end,
            limit=limit,
        )

    @agent.tool_plain
    def search_docs(query: str, limit: int = 10) -> dict[str, Any]:
        """Semantic search over ingested documentation chunks. Returns chunks
        with content, source_path, metadata. Limit capped at 10."""
        return agent_tools.search_docs(query=query, limit=limit)

    @agent.tool
    def search_past_incidents(
        ctx: RunContext[AgentDeps],
        query: str,
        limit: int = 5,
        min_similarity: float = 0.75,
    ) -> list[dict[str, Any]]:
        """Find prior incident reports semantically similar to the query.
        Excludes the current session. Returns up to ``limit`` matches with
        session_id, report_id, question, summary, root_cause, created_at,
        similarity — empty list if nothing crosses ``min_similarity``."""
        results = incident_memory.search_past_incidents(
            query,
            current_session_id=ctx.deps.session_id,
            limit=limit,
            min_similarity=min_similarity,
        )
        return [
            {
                "session_id": r.session_id,
                "report_id": r.report_id,
                "question": r.question,
                "summary": r.summary,
                "root_cause": r.root_cause,
                "created_at": r.created_at,
                "similarity": r.similarity,
            }
            for r in results
        ]

    @agent.tool_plain
    def grep_repo(
        pattern: str,
        glob: str | None = None,
        max_results: int = 50,
        context_lines: int = 2,
    ) -> dict[str, Any]:
        """Search source code by ripgrep regex over KNOWLEDGE_CODE_SOURCES.
        Use for literal lookups: error strings, function names from stack traces,
        service identifiers, file paths. Returns hits with path, line, snippet,
        and before/after context."""
        return agent_tools.grep_repo(
            pattern=pattern,
            glob=glob,
            max_results=max_results,
            context_lines=context_lines,
        )

    @agent.tool_plain
    def read_file(
        path: str,
        line_start: int = 1,
        line_end: int | None = None,
    ) -> dict[str, Any]:
        """Read a bounded slice of a source file under the KNOWLEDGE_CODE_SOURCES
        allowlist. Chain after grep_repo to inspect context. line_end is
        inclusive; omit it to read to EOF (capped at 2000 lines)."""
        return agent_tools.read_file(
            path=path,
            line_start=line_start,
            line_end=line_end,
        )

    return agent


def generate_incident_report(
    session_id: str,
    question: str,
    *,
    report_id: str | None = None,
) -> dict[str, Any]:
    """Run the agent for ``session_id`` + ``question``; persist and return
    ``{"report_id": str, "content": str}``.

    If ``report_id`` is provided, the existing report row is updated;
    otherwise a new one is created. Raises ``ValueError`` on missing
    LLM_API_KEY or unknown report_id.
    """
    if not config.LLM_API_KEY:
        raise ValueError("LLM_API_KEY not set")

    agent = _make_agent()
    deps = AgentDeps(session_id=session_id)

    result = agent.run_sync(
        f"Investigation question: {question}",
        deps=deps,
    )
    report = result.output
    content = render_markdown(report)

    repo = ReportRepository()
    if report_id is not None:
        if not repo.update_content(report_id, session_id, content):
            raise ValueError("Report not found for update")
        existing = repo.get_by_id(report_id, session_id=session_id)
        final_report_id = report_id
        final_created_at = existing.created_at if existing else ""
    else:
        created = repo.create(session_id=session_id, content=content)
        final_report_id = created.id
        final_created_at = created.created_at

    # Post-success indexing into cross-session incident memory. Failure here
    # must never propagate — the user-visible report has already landed.
    incident_memory.index_report(
        session_id=session_id,
        report_id=final_report_id,
        question=question,
        created_at=final_created_at,
        report=report,
    )

    return {"report_id": final_report_id, "content": content}


# ---------------------------------------------------------------------------
# Back-compat: a few callers (tests, MCP docs) historically imported these.
# ---------------------------------------------------------------------------

#: Kept as a stable re-export so callers don't have to chase the renamed module.
SYSTEM_PROMPT = AGENT_INSTRUCTIONS

__all__ = [
    "AGENT_INSTRUCTIONS",
    "AgentDeps",
    "IncidentReport",
    "REPORT_SECTIONS",
    "SYSTEM_PROMPT",
    "generate_incident_report",
    "render_markdown",
]
