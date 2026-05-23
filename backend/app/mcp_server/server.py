"""LogPilot MCP server (FastMCP, stdio).

Tools delegate to the same service functions the in-process PydanticAI agent
will use, so behavior stays consistent across both surfaces. All tools are
read-only with the single exception of `generate_incident_report`, which
creates a new report row but never mutates logs or sessions.

Discoverable from any MCP client. Example client config (Claude Code):

    {
      "mcpServers": {
        "logpilot": {
          "command": "uv",
          "args": ["run", "python", "-m", "app.mcp_server"],
          "cwd": "/path/to/logpilot/backend"
        }
      }
    }
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.lib.repositories import SessionRepository
from app.services import agent as agent_service
from app.services import agent_tools

logger = logging.getLogger(__name__)

mcp = FastMCP("logpilot")


# ---------------------------------------------------------------------------
# Read-only investigation tools (one-to-one with the in-process agent tools)
# ---------------------------------------------------------------------------


@mcp.tool()
def query_logs(
    session_id: str,
    query: str = "",
    start: str | None = None,
    end: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Query the session's log store. Returns entries with timestamp, level,
    service, and raw_message. start/end are ISO 8601; limit is capped at 1000."""
    return agent_tools.query_logs(
        session_id=session_id,
        query=query,
        start=start,
        end=end,
        limit=limit,
    )


@mcp.tool()
def query_metrics(
    session_id: str,
    metric_name: str,
    start: str,
    end: str,
    step: str = "15s",
) -> dict[str, Any]:
    """Query derived Prometheus metrics for the session (e.g. errors_total,
    error_rate, response_time). start/end ISO 8601; step is a Prometheus step."""
    return agent_tools.query_metrics(
        session_id=session_id,
        metric_name=metric_name,
        start=start,
        end=end,
        step=step,
    )


@mcp.tool()
def search_docs(query: str, limit: int = 10) -> dict[str, Any]:
    """Semantic search over ingested documentation chunks. Returns chunks with
    content, source_path, and metadata. Limit capped at 10."""
    return agent_tools.search_docs(query=query, limit=limit)


@mcp.tool()
def grep_repo(
    pattern: str,
    glob: str | None = None,
    max_results: int = 50,
    context_lines: int = 2,
) -> dict[str, Any]:
    """Search source code by ripgrep regex over configured KNOWLEDGE_CODE_SOURCES.
    Use for literal lookups: error strings, function names from stack traces,
    service identifiers, file paths. Returns hits with path, line, snippet, and
    before/after context."""
    return agent_tools.grep_repo(
        pattern=pattern,
        glob=glob,
        max_results=max_results,
        context_lines=context_lines,
    )


@mcp.tool()
def read_file(
    path: str,
    line_start: int = 1,
    line_end: int | None = None,
) -> dict[str, Any]:
    """Read a bounded slice of a source file under the KNOWLEDGE_CODE_SOURCES
    allowlist. Chain after grep_repo to inspect context. line_end is inclusive;
    omit it to read to EOF (capped at 2000 lines)."""
    return agent_tools.read_file(
        path=path,
        line_start=line_start,
        line_end=line_end,
    )


# ---------------------------------------------------------------------------
# Report generation (calls the same agent the web app does)
# ---------------------------------------------------------------------------


@mcp.tool()
def generate_incident_report(session_id: str, question: str) -> dict[str, Any]:
    """Run the incident-investigation agent against `session_id` with the given
    question. Returns {report_id, content} where content is the structured
    Markdown report. Creates a new report row in the session."""
    return agent_service.generate_incident_report(session_id, question)


# ---------------------------------------------------------------------------
# Session metadata (read-only)
# ---------------------------------------------------------------------------


@mcp.tool()
def list_sessions() -> dict[str, Any]:
    """List every session with its id, name, external_link, pin state, and
    timestamps. Use to discover available sessions before calling query_logs
    or generate_incident_report."""
    sessions = SessionRepository().list_all()
    return {"sessions": [s.to_api() for s in sessions]}


@mcp.tool()
def get_session(session_id: str) -> dict[str, Any]:
    """Fetch one session's metadata. Returns {"error": ...} if not found."""
    session = SessionRepository().get(session_id)
    if session is None:
        return {"error": "Session not found"}
    return session.to_api()
