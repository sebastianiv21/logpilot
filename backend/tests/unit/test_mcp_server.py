"""Unit tests for the LogPilot MCP server registration and tool delegation.

We don't spin up a real stdio transport here — these are static checks that
the FastMCP instance registers every tool we expect, with reasonable schemas
and docstrings derived from the wrapper functions.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.mcp_server.server import mcp

EXPECTED_TOOLS = {
    "query_logs",
    "query_metrics",
    "search_docs",
    "grep_repo",
    "read_file",
    "generate_incident_report",
    "list_sessions",
    "get_session",
}


@pytest.mark.anyio
async def test_every_expected_tool_is_registered():
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert EXPECTED_TOOLS.issubset(names), (
        f"missing tools: {EXPECTED_TOOLS - names}"
    )


@pytest.mark.anyio
async def test_every_tool_has_description():
    tools = await mcp.list_tools()
    for tool in tools:
        assert tool.description, f"tool {tool.name} has no description"
        assert len(tool.description) > 20, (
            f"tool {tool.name} description too short: {tool.description!r}"
        )


@pytest.mark.anyio
async def test_grep_repo_delegates_to_agent_tools():
    with patch("app.mcp_server.server.agent_tools.grep_repo") as mocked:
        mocked.return_value = {"hits": [], "code_search_unavailable": False}
        result = await mcp.call_tool(
            "grep_repo",
            {"pattern": "KafkaTimeoutException", "glob": "*.py"},
        )
        mocked.assert_called_once_with(
            pattern="KafkaTimeoutException",
            glob="*.py",
            max_results=50,
            context_lines=2,
        )
        # Result is a (content, structured) tuple; structured payload echoes the dict.
        assert result is not None


@pytest.mark.anyio
async def test_list_sessions_uses_repository():
    with patch("app.mcp_server.server.SessionRepository") as mocked_repo:
        mocked_repo.return_value.list_all.return_value = []
        result = await mcp.call_tool("list_sessions", {})
        assert result is not None
        mocked_repo.return_value.list_all.assert_called_once()


class TestEntrypointDatabaseSetup:
    """The stdio entrypoint must mirror the FastAPI lifespan: init the DB at
    startup, close the pool at shutdown — but never abort startup if the DB is
    unavailable, so grep_repo / read_file remain usable for lightweight tests.
    """

    def test_setup_database_returns_true_on_success(self):
        from app.mcp_server import __main__ as entrypoint

        with patch.object(entrypoint, "initialize_schema") as init_schema, \
             patch.object(entrypoint, "init_pool") as init_pool:
            assert entrypoint._setup_database() is True
            init_schema.assert_called_once()
            init_pool.assert_called_once()

    def test_setup_database_returns_false_when_db_unavailable(self, caplog):
        from app.mcp_server import __main__ as entrypoint

        with patch.object(
            entrypoint, "initialize_schema",
            side_effect=RuntimeError("DATABASE_URL is not set"),
        ):
            assert entrypoint._setup_database() is False
        # Warning must mention which tools degrade.
        assert any(
            "grep_repo" in record.message and "read_file" in record.message
            for record in caplog.records
        )

    def test_main_closes_pool_even_when_run_raises(self):
        from app.mcp_server import __main__ as entrypoint

        with patch.object(entrypoint, "_setup_database", return_value=True), \
             patch.object(entrypoint.mcp, "run", side_effect=KeyboardInterrupt), \
             patch.object(entrypoint, "close_pool") as close:
            with pytest.raises(KeyboardInterrupt):
                entrypoint.main()
            close.assert_called_once()
