"""LogPilot MCP server — exposes incident-investigation tools to MCP clients.

External agents (Claude Code, Cursor, Hermes, etc.) connect via stdio and can
call the same tools the in-process PydanticAI agent uses: query_logs,
query_metrics, search_docs, grep_repo, read_file, generate_incident_report,
plus read-only session metadata.

Module is named ``mcp_server`` (not ``mcp``) to avoid colliding with the
upstream ``mcp`` SDK package — ``pyproject.toml`` adds ``app/`` to
``pythonpath``, which puts our packages at the top level.

Run with:
    python -m app.mcp_server
"""

from .server import mcp

__all__ = ["mcp"]
