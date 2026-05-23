# LogPilot Backend

## Run dev server

From the `backend` directory:

```bash
uv run fastapi dev app/main.py
```

The FastAPI CLI expects a file path (not `app.main:app`). It looks for an `app` variable in that file by default.

## MCP server

LogPilot exposes its investigation tools to any MCP client (Claude Code, Cursor, Hermes, etc.) over stdio. The server wraps the same functions the in-process agent uses, so calling `grep_repo` or `generate_incident_report` from an external agent behaves the same as from the web app.

Run it directly:

```bash
uv run python -m app.mcp_server
```

Wire it into Claude Code via `~/.claude.json` (or equivalent):

```json
{
  "mcpServers": {
    "logpilot": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp_server"],
      "cwd": "/path/to/logpilot/backend"
    }
  }
}
```

Tools exposed: `query_logs`, `query_metrics`, `search_docs`, `grep_repo`, `read_file`, `generate_incident_report`, `list_sessions`, `get_session`. The server needs the same env vars the backend does (`DATABASE_URL`, `LOKI_URL`, `LLM_API_KEY`, `KNOWLEDGE_CODE_SOURCES`, etc.) — easiest is to launch from a shell that already has them set.

## PDF export

Report export to PDF uses ReportLab and streams the generated file back to the client from a spooled temporary file, which avoids creating an extra in-memory `bytes` copy in the API layer.

The backend also logs one structured `pdf_export` event per request with content-free diagnostics such as report size, code-fence counts, parsed block counts, render duration, and before/after process max RSS. Oversized or pathological inputs are rejected with a deterministic API error so the Markdown export remains available as a safe fallback.
