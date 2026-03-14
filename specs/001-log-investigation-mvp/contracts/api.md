# API Contract: Log Investigation MVP

**Branch**: `001-log-investigation-mvp` | **Date**: 2025-03-13

Public HTTP API surface for the backend. All endpoints are relative to a base URL (e.g. `http://localhost:8000`). Request/response formats are JSON unless noted.

---

## Base

- **Content-Type**: `application/json` for request/response bodies where applicable.
- **Errors**: On failure, return appropriate HTTP status and a body with at least `detail` (string or list of error items). Use 400 for validation/archive errors, 404 for missing session/report, 413 for payload too large, 422 for unprocessable.

---

## Sessions

### List sessions

- **GET** `/sessions`
- **Response**: `200`
  - Body: `{ "sessions": [ { "id": "<uuid>", "name": "<string|null>", "external_link": "<string|null>", "created_at": "<ISO8601>", "updated_at": "<ISO8601>" } ] }`
  - List MUST identify each session by at least creation time and/or external link; if name is set, include it.

### Create session

- **POST** `/sessions`
- **Body**: `{ "name": "<string|null>", "external_link": "<string|null>" }` (both optional)
- **Response**: `201`
  - Body: `{ "id": "<uuid>", "name": "<string|null>", "external_link": "<string|null>", "created_at": "<ISO8601>", "updated_at": "<ISO8601>" }`

### Get session

- **GET** `/sessions/{session_id}`
- **Response**: `200` — same shape as single session object; `404` if not found.

### Update session

- **PATCH** `/sessions/{session_id}`
- **Body**: `{ "name": "<string|null>", "external_link": "<string|null>" }` (partial; only provided fields updated)
- **Response**: `200` — updated session object; `404` if not found.

### Set current session (optional, deferred for MVP)

- **MVP**: Session scoping is **path-only**. All endpoints that need a session require `session_id` in the path (e.g. `POST /sessions/{session_id}/logs/upload`, `GET /sessions/{session_id}/reports`). Clients pass the session id in the URL for each request; no "current session" state is required.
- **Post-MVP (optional)**: A future revision may add **POST** `/sessions/current` (body: `session_id`) or **Header** `X-Session-Id: <uuid>` so that clients can set a default session and call session-scoped endpoints without repeating the id in every path. Until then, the contract is satisfied by path-only session selection.

---

## Upload

### Upload log archive

- **POST** `/sessions/{session_id}/logs/upload`
- **Content-Type**: `multipart/form-data`; field name for file: e.g. `file`.
- **Constraints**: Archive size ≤ 100 MB compressed and ≤ 500 MB uncompressed (reject with 413 or 400 and structured message if exceeded).
- **Response**: `200` on success/partial
  - Body: `{ "status": "success"|"partial"|"failed", "files_processed": <int>, "files_skipped": <int>, "lines_parsed": <int>, "lines_rejected": <int>, "session_id": "<uuid>", "error": "<string|null>" }`
- **Error**: `400` for invalid/malformed archive or validation failure; `404` if session not found; `413` when size limit exceeded. Body MUST include clear, structured error message.

---

## Reports

### List reports for session

- **GET** `/sessions/{session_id}/reports`
- **Response**: `200`
  - Body: `{ "reports": [ { "id": "<uuid>", "session_id": "<uuid>", "created_at": "<ISO8601>" } ] }` (content may be omitted for list)

### Generate report (user-triggered)

- **POST** `/sessions/{session_id}/reports/generate`
- **Body**: `{ "question": "<natural-language incident question>" }`
- **Response**: `202` Accepted (async) or `200` (sync) with report id and optionally content.
  - Body: `{ "id": "<uuid>", "session_id": "<uuid>", "created_at": "<ISO8601>", "content": "<markdown>|null" }`
- **Behavior**: Agent uses only approved tools; returns structured report; report stored in session.

### Get report

- **GET** `/sessions/{session_id}/reports/{report_id}`
- **Response**: `200` — `{ "id": "<uuid>", "session_id": "<uuid>", "content": "<markdown>", "created_at": "<ISO8601>" }`; `404` if not found.

### Export report

- **GET** `/sessions/{session_id}/reports/{report_id}/export?format=markdown|pdf`
- **Response**: `200`
  - `format=markdown`: body is Markdown (e.g. `Content-Type: text/markdown`).
  - `format=pdf`: body is PDF (e.g. `Content-Type: application/pdf`); `Content-Disposition: attachment; filename="report-<id>.pdf"`.
- **404** if session or report not found.

---

## Knowledge base

### Trigger ingestion

- **POST** `/knowledge/ingest`
- **Body**: `{ "sources": [ "<path>", ... ] }` or config-driven paths; exact schema TBD (e.g. docs path, repo path).
- **Response**: `202` Accepted or `200` — ingestion is repeatable; index refreshed.

### Search (optional for API; used by agent)

- **POST** `/knowledge/search`
- **Body**: `{ "query": "<string>", "limit": <int> }`
- **Response**: `200` — `{ "chunks": [ { "content": "<text>", "source_path": "<string>", "metadata": {} } ] }`

---

## Log and metric queries

These may be internal (agent only) or exposed for UI. If exposed:

- **POST** `/sessions/{session_id}/logs/query` — body: time range, label filters; response: log lines (schema per Parsed Log Record).
- **POST** `/sessions/{session_id}/metrics/query` — body: metric name(s), time range; response: time series or scalar values.

Exact request/response schemas can be aligned with Loki/Prometheus query APIs or simplified; document in backend API spec.
