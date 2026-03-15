# API Contract: Frontend-Consumed Backend API

**Branch**: `002-frontend-implementation`  
**Date**: 2026-03-14  
**Purpose**: Contract between the LogPilot frontend (Vite + React SPA) and the existing FastAPI backend. All endpoints are relative to a configurable base URL (e.g. `VITE_API_BASE=http://localhost:8000`).

---

## Base

- **Content-Type**: `application/json` for request/response bodies unless noted.
- **CORS**: Backend allows origins `*`; credentials and all methods/headers allowed.
- **Errors**: JSON body with `detail` (string or array of validation errors). Status: 400 validation/archive, 404 not found, 409 conflict (e.g. report not ready, ingest in progress), 413 payload too large, 422 validation, 503 service unavailable (e.g. LLM not configured).

---

## Root

- **GET** `/`
- **Response**: `200` — `{ "status": "ok", "service": "logpilot-backend" }` (health/identity).

---

## Sessions

- **GET** `/sessions`  
  **Response**: `200` — `{ "sessions": [ { "id", "name", "external_link", "created_at", "updated_at" } ] }`

- **POST** `/sessions`  
  **Body**: `{ "name": string | null, "external_link": string | null }` (optional)  
  **Response**: `201` — single session object.

- **GET** `/sessions/{session_id}`  
  **Response**: `200` — session object; `404` if not found.

- **PATCH** `/sessions/{session_id}`  
  **Body**: `{ "name": string | null, "external_link": string | null }` (partial)  
  **Response**: `200` — updated session; `404` if not found.

---

## Upload

- **POST** `/sessions/{session_id}/logs/upload`  
  **Content-Type**: `multipart/form-data`; field name: `file`; file must be `.zip`.  
  **Response**: `200` — `{ "status": "success"|"failed", "files_processed", "files_skipped", "lines_parsed", "lines_rejected", "session_id", "error": string | null }`  
  **Errors**: `400` invalid file type/malformed; `404` session not found; `413` archive exceeds limit (e.g. 100 MB).

---

## Logs query

- **POST** `/sessions/{session_id}/logs/query`  
  **Body**: `{ "start": string | null, "end": string | null, "limit": number (default 100, max 1000), "service": string | null, "environment": string | null, "log_level": string | null }` (ISO 8601 for start/end)  
  **Response**: `200` — `{ "logs": [ { "timestamp_ns": number, "raw_message": string, ...labels } ] }`  
  **Errors**: `400` invalid time format; `404` session not found.

- **GET** `/sessions/{session_id}/logs/range`  
  **Response**: `200` — `{ "from_ms": number, "to_ms": number }` (time extent of session logs in milliseconds since epoch; for Grafana Explore `from`/`to`).  
  **Errors**: `404` session not found or no logs for session.

---

## Reports

- **GET** `/sessions/{session_id}/reports`  
  **Response**: `200` — `{ "reports": [ { "id", "session_id", "created_at" } ] }`; `404` if session not found.

- **GET** `/sessions/{session_id}/reports/{report_id}`  
  **Response**: `200` — `{ "id", "session_id", "content", "created_at" }` (content empty string while generating); `404` if not found.

- **POST** `/sessions/{session_id}/reports/generate`  
  **Body**: `{ "question": string }` (min length 1)  
  **Response**: `202` — `{ "id", "session_id", "created_at", "content": null }`. Client must poll GET report until content is present.  
  **Errors**: `404` session not found; `503` LLM not configured.

- **GET** `/sessions/{session_id}/reports/{report_id}/export?format=markdown|pdf`  
  **Response**: `200` — body is Markdown (`text/markdown`) or PDF (`application/pdf`) with `Content-Disposition: attachment`.  
  **Errors**: `404` not found; `409` report content not yet ready (poll GET report first).

---

## Knowledge

- **POST** `/knowledge/ingest`  
  **Body**: `{ "sources": string[] }` (optional; if empty, backend uses configured KNOWLEDGE_SOURCES)  
  **Response**: `202` — `{ "message": "..." }`. Client must poll GET ingest status.  
  **Errors**: `400` no sources; `409` ingest already in progress; `503` embeddings not configured.

- **GET** `/knowledge/ingest/status`  
  **Response**: `200` — `{ "status": "running"|"idle", "last_result": { "chunks_ingested", "files_processed" } | null, "error": string | null }`

- **POST** `/knowledge/search`  
  **Body**: `{ "query": string, "limit": number (1–100, default 10) }`  
  **Response**: `200` — `{ "chunks": [ { "content", "source_path", "metadata" } ] }`  
  **Errors**: `503` search unavailable (LLM not set).

---

## Metrics / dashboards (external)

The frontend does not call the backend for metrics UI. It opens a **link** to Grafana (or configured dashboard URL) in a new tab, with session context (e.g. query param `var-session_id=<session_id>`). Grafana URL is frontend-configurable (e.g. `VITE_GRAFANA_URL=http://localhost:3000`). No API contract between frontend and Grafana beyond URL and optional query params.
