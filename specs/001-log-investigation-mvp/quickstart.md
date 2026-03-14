# Quickstart: Log Investigation MVP

**Branch**: `001-log-investigation-mvp` | **Date**: 2025-03-13

Minimal steps to run the full stack locally and validate the feature. Use this for development and manual testing.

---

## Prerequisites

- Docker and Docker Compose
- Python 3.14+ (for local backend development)
- LLM API key (OpenAI, OpenRouter, or any OpenAI-compatible endpoint) — set in environment

---

## 1. Start infrastructure

From the repository root:

```bash
docker compose up -d
```

This brings up:

- **Loki** — log store (e.g. port 3100)
- **Prometheus** — metrics (e.g. port 9090)
- **Grafana** — dashboards (e.g. port 3000; default login admin/admin)
- **Qdrant** — vector store for knowledge base (e.g. port 6333)

Backend can run in Docker or on the host (see below).

---

## 2. Configure and run the backend

- Copy or create `.env` from `.env.example` (or document required vars in README).
- Required:
  - `LLM_API_KEY` — API key for the chosen provider
  - `LLM_BASE_URL` — (optional) Base URL for OpenAI-compatible API; omit for OpenAI
  - `LLM_MODEL` — (optional) Model name; default per provider
  - `LOKI_URL` — e.g. `http://localhost:3100`
  - `PROMETHEUS_URL` — e.g. `http://localhost:9090`
  - `QDRANT_URL` — e.g. `http://localhost:6333`
  - `DATA_DIR` — (optional) Directory for SQLite and temp extraction; default e.g. `./data`

From the repository root, start the backend dev server:

```bash
cd backend && uv run fastapi dev app/main.py
```

API base URL: `http://localhost:8000`. Then create a session and upload a log archive:

```bash
# Create session
curl -X POST http://localhost:8000/sessions -H "Content-Type: application/json" -d '{"name":"my-ticket"}'

# Upload (replace SESSION_ID and use path to a .zip)
curl -X POST http://localhost:8000/sessions/SESSION_ID/logs/upload -F "file=@/path/to/logs.zip"
```

---

## 3. View logs and metrics

- **Grafana**: Open http://localhost:3000. Use Explore for Loki (log queries) and for Prometheus (metrics). Dashboards are auto-provisioned; select the session scope (e.g. via label `session_id` or current session).
- **Upload result**: The upload response includes `files_processed`, `files_skipped`, `lines_parsed`, `lines_rejected`.

---

## 4. Knowledge base (optional)

- Configure docs/repo paths (e.g. in config or `.env`).
- Trigger ingestion:

```bash
curl -X POST http://localhost:8000/knowledge/ingest -H "Content-Type: application/json" -d '{"sources":["/path/to/docs"]}'
```

---

## 5. Generate and export a report

- Generate report for the current session:

```bash
curl -X POST http://localhost:8000/sessions/SESSION_ID/reports/generate -H "Content-Type: application/json" -d '{"question":"Why did the service fail?"}'
```

- List reports. Report generation runs in the background; poll until content is present, then export (Markdown or PDF):

```bash
# Poll until content is non-empty: GET .../reports/REPORT_ID
curl -o report.md "http://localhost:8000/sessions/SESSION_ID/reports/REPORT_ID/export?format=markdown"
curl -o report.pdf "http://localhost:8000/sessions/SESSION_ID/reports/REPORT_ID/export?format=pdf"
```

(Export returns 409 until the report has content.)

---

## Archive conventions and limits

- **Size**: Max 500 MB uncompressed, 100 MB compressed. Larger uploads are rejected with a clear error.
- **Log file patterns**: `.log`, `.csv`, `.json`, and optionally `.log.*`, `stdout`, `stderr`. Other entries are skipped; count in upload result.
- **Service/environment labels**: Path-based convention (e.g. `logs/<service>/<env>/...`). If structure does not match, a single upload-scoped label is used; see [data-model.md](./data-model.md) and [research.md](./research.md).

---

## Running tests

From repository root:

```bash
cd backend && pytest
```

Contract tests validate API and agent tool schemas; see `specs/001-log-investigation-mvp/contracts/`.

---

## Troubleshooting

- **Upload 413 or "archive too large"**: Respect 100 MB compressed / 500 MB uncompressed limit.
- **Upload returns NetworkError or request never appears in server logs**: If you open the API through a **tunnel** (e.g. Cursor port forwarding, cloud proxy), POST requests with a body are often dropped or not forwarded. Use **localhost** in the browser (`http://localhost:8000/docs`) when the browser and backend run on the same machine, or test upload with **curl** from the same host: `curl -X POST http://localhost:8000/sessions/SESSION_ID/logs/upload -F "file=@path/to/logs.zip"`.
- **No logs in Grafana**: Confirm session_id in Loki labels; check upload response for `lines_parsed` > 0.
- **Agent "knowledge not available"**: Run knowledge ingestion and ensure Qdrant is up.
- **PDF export fails**: Ensure PDF dependency (e.g. weasyprint) is installed; see backend README.
