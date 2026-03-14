# LogPilot

Local-first log investigation platform: upload compressed log archives, parse and store in Loki, derive metrics for Prometheus, provision Grafana dashboards, index docs/repo in Qdrant, and use an AI agent to produce structured incident reports. Full stack runs via Docker Compose; reports are exportable as Markdown or PDF.

## Prerequisites

- **Docker** and **Docker Compose**
- **Python 3.14+** (for local backend development; optional if you only run the stack in Docker)
- **LLM API key** (OpenAI, OpenRouter, or any OpenAI-compatible endpoint) for report generation

## Quick start

1. **Copy environment file** and set at least `LLM_API_KEY`:

   ```bash
   cp .env.example .env
   # Edit .env and set LLM_API_KEY (and optionally LLM_BASE_URL, LLM_MODEL)
   ```

2. **Start the stack** (Loki, Prometheus, Grafana, Qdrant, backend):

   ```bash
   docker compose up -d
   ```

3. **Create a session and upload logs** (see [Quickstart](specs/001-log-investigation-mvp/quickstart.md) for full flow):

   ```bash
   curl -X POST http://localhost:8000/sessions -H "Content-Type: application/json" -d '{"name":"my-ticket"}'
   curl -X POST http://localhost:8000/sessions/SESSION_ID/logs/upload -F "file=@/path/to/logs.zip"
   ```

- **API docs**: http://localhost:8000/docs  
- **Grafana**: http://localhost:3000 (admin/admin)

For detailed steps (knowledge ingest, report generation, export), see **[Quickstart](specs/001-log-investigation-mvp/quickstart.md)**. Report generation is asynchronous; export returns 409 until the report has content—poll `GET /sessions/{id}/reports/{report_id}` until `content` is non-empty, then export.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LLM_API_KEY` | Yes (for reports) | API key for OpenAI-compatible LLM |
| `LLM_BASE_URL` | No | Base URL for LLM API; omit for OpenAI |
| `LLM_MODEL` | No | Model name (default: `gpt-4o-mini`) |
| `EMBEDDING_MODEL` | No | Embedding model (default: `text-embedding-3-small`) |
| `LOKI_URL` | No* | Loki URL (default: `http://localhost:3100`) |
| `PROMETHEUS_URL` | No* | Prometheus URL (default: `http://localhost:9090`) |
| `QDRANT_URL` | No* | Qdrant URL (default: `http://localhost:6333`) |
| `DATA_DIR` | No | Directory for SQLite and temp files (default: `./data`) |
| `KNOWLEDGE_SOURCES` | No | Comma-separated paths for knowledge ingest |
| `KNOWLEDGE_SOURCES_MOUNT` | No | Docker: parent path mounted at `/knowledge` for multiple sources |

\* Defaults are correct when running the backend on the host against `docker compose` services; in Docker, the compose file sets URLs to service names.

Copy `.env.example` to `.env` and set the values you need.

## Running the backend locally

Useful when developing; infrastructure can still run in Docker:

```bash
docker compose up -d loki prometheus grafana qdrant
cd backend && uv run fastapi dev app/main.py
```

Set `LOKI_URL`, `PROMETHEUS_URL`, `QDRANT_URL` in `.env` to `http://localhost:3100`, etc.

## Running tests

From the repository root:

```bash
cd backend && pytest
```

Contract tests validate API and agent tool schemas (see `specs/001-log-investigation-mvp/contracts/`).

## Archive limits and conventions

- **Size**: Max 500 MB uncompressed, 100 MB compressed per upload.
- **Log patterns**: `.log`, `.csv`, `.json`, and optionally `.log.*`, `stdout`, `stderr`. Other files are skipped and counted in the upload result.

## Documentation

- [Quickstart](specs/001-log-investigation-mvp/quickstart.md) — full flow: compose, session, upload, Grafana, knowledge ingest, report generation, export  
- [Implementation plan](specs/001-log-investigation-mvp/plan.md) — tech stack and project structure  
- [API contracts](specs/001-log-investigation-mvp/contracts/) — API and agent tool specs  
