"""Stdio entrypoint for the LogPilot MCP server.

    python -m app.mcp_server
"""

from app.mcp_server.server import mcp


def main() -> None:
    # FastMCP defaults to stdio when no transport is passed.
    mcp.run()


if __name__ == "__main__":
    main()
