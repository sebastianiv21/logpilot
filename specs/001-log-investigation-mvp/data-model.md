# Data Model: Log Investigation MVP

**Branch**: `001-log-investigation-mvp` | **Date**: 2025-03-13

Entities and their fields, relationships, validation rules, and state. Used for backend implementation and API contracts.

---

## 1. Session

Logical container for an investigation or support ticket. Logs and derived metrics are scoped to a session; uploads within a session are additive.

| Field | Type | Required | Validation / Notes |
|-------|------|----------|--------------------|
| id | string (UUID) | yes | Generated on create |
| name | string | no | Optional label (e.g. ticket ID); shown in list if set |
| external_link | string (URL) | no | Optional link (Slack, Zendesk, any URL); stored and visible in list/detail |
| created_at | datetime (ISO 8601) | yes | Set on create |
| updated_at | datetime (ISO 8601) | yes | Updated on any change |

**Relationships**: One session has many uploads (implicit via Loki labels), many derived metric series (scoped by session label), and many incident reports.

**Identification in list**: Each session MUST be identifiable by at least creation time and/or external link; if name is set, it MUST be shown.

**State**: No formal state machine; sessions are created and optionally updated (name, link). “Current” or “selected” session is a UI/API concept (e.g. query param or header).

---

## 2. Log Archive (Input)

Not persisted as an entity; input to the upload flow. Described here for contract and validation.

- **Format**: Compressed archive (e.g. `.zip`).
- **Size limits**: 500 MB uncompressed, 100 MB compressed (MVP); reject with structured error if exceeded.
- **Structure**: Path-based (e.g. `logs/<service>/...` or `logs/<service>/<env>/...`) or flat; service and environment labels derived per documented conventions or fallback to single upload-scoped label.
- **Log file patterns**: Entries matching `.log`, `.csv`, `.json`, and optionally `.log.*` or names like `stdout`/`stderr` are processed as log files; others are skipped and count reported.

---

## 3. Parsed Log Record (Normalized)

Stored in Loki; not in application DB. Canonical schema used for ingestion and query.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| timestamp | datetime (nanoseconds for Loki) | yes | Parsed or ingest time |
| log_level | string | yes | e.g. DEBUG, INFO, WARN, ERROR; or "unknown" |
| service | string | yes | From path or upload-scoped |
| environment | string | no | From path if present; else empty/unknown |
| raw_message | string | yes | Original log line preserved |
| source_file | string | no | Original filename in archive |
| session_id | string | yes | For scoping queries |

**Labels (Loki)**: At least `service`, `environment`, `log_level`, `session_id` (or equivalent) for querying. Additional labels (e.g. batch) optional.

**Validation**: Unparseable lines are counted and reported; they do not fail the upload. Parsed lines must have timestamp (or fallback), level, service, and raw_message.

---

## 4. Upload Result (Output)

Returned by the upload API; not stored as a standalone entity (may be stored in session activity or logs if desired).

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| status | enum | yes | success | partial | failed |
| files_processed | int | yes | Count of files treated as log files |
| files_skipped | int | yes | Count of entries not matching log patterns |
| lines_parsed | int | yes | Successfully parsed lines |
| lines_rejected | int | yes | Unparseable lines (per-file or total) |
| session_id | string | yes | Session this upload was applied to |
| error | string | no | Present when status is failed; structured message |

---

## 5. Derived Metric

Numeric measures from log events; exposed to Prometheus and Grafana. Stored in Prometheus (or pushed by backend); scoped by session (e.g. label `session_id` or equivalent).

**Metrics (MVP)**:

- `errors_total` — counter
- `requests_total` — counter  
- `error_rate` — gauge or derived
- `response_time_*` — histogram when latency present in logs

**Fields (conceptual)**: metric name, value(s), timestamp, labels (at least session_id). When a metric is not derivable (e.g. no latency field), that metric is skipped with status feedback; pipeline does not fail.

---

## 6. Dashboard

Pre-provisioned views (Grafana); not an application entity. At least one default dashboard showing error rate, request volume, error distribution, log volume, anomalies over time. Data scoped to current/selected session via datasource or query params.

---

## 7. Knowledge Chunk

Segment of documentation or repository content in Qdrant.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | yes | Qdrant point id |
| content | text | yes | Chunk text |
| embedding | vector | yes | From configured embedding model |
| source_path | string | no | File path or doc identifier |
| document_type | string | no | e.g. markdown, runbook, source |
| metadata | map | no | Additional source metadata |

**Relationships**: Retrieved by semantic search; shared across sessions (not session-scoped). Ingestion is repeatable; user can re-ingest when docs/repo change.

---

## 8. Incident Report

Structured output from the AI agent; stored per session.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string (UUID) | yes | Generated on create |
| session_id | string (UUID) | yes | FK to Session |
| content | text | yes | Full report (Markdown) with required sections |
| created_at | datetime (ISO 8601) | yes | When generated |

**Required sections in content**: Incident Summary, Possible Root Cause, Supporting Evidence, Recommended Fix, next troubleshooting steps (and everything needed to resolve the issue). Evidence should reference logs, metrics, and knowledge sources where relevant.

**Export**: User selects which report (e.g. latest or by id), then format (Markdown or PDF); exported file contains that single report.

**State**: Report is immutable once generated; report history allows comparison for the same ticket/session.

---

## 9. Session Metadata Store (SQLite)

Tables used for session and report metadata (see research.md).

- **sessions**: id (PK), name, external_link, created_at, updated_at
- **reports**: id (PK), session_id (FK), content, created_at

Logs and metrics live in Loki and Prometheus; knowledge in Qdrant. “Current session” can be stored in memory or a simple store (e.g. default session id in config or last-used in a small state file).
