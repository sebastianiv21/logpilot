"""Stdio entrypoint for the LogPilot MCP server.

    python -m app.mcp_server
"""

from __future__ import annotations

import logging

from app.lib.db import close_pool, init_pool, initialize_schema
from app.mcp_server.server import mcp

logger = logging.getLogger(__name__)


def _setup_database() -> bool:
    """Mirror the FastAPI lifespan hook: schema init + pool open.

    Returns True if the DB is ready, False otherwise. We don't abort on
    failure — the no-DB tools (grep_repo, read_file) should still work so the
    server is useful for lightweight code-search even without a database
    configured.
    """
    try:
        initialize_schema()
        init_pool()
    except Exception as exc:
        logger.warning(
            "MCP server starting WITHOUT database connectivity (%s). "
            "DB-backed tools (query_logs, query_metrics, search_docs, "
            "list_sessions, get_session, generate_incident_report) will fail; "
            "grep_repo and read_file remain available.",
            exc,
        )
        return False
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    _setup_database()
    try:
        # FastMCP defaults to stdio when no transport is passed.
        mcp.run()
    finally:
        close_pool()


if __name__ == "__main__":
    main()
