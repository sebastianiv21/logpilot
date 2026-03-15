# Data Model: Log Investigation Frontend

**Branch**: `002-frontend-implementation`  
**Date**: 2026-03-14  
**Source**: Feature spec entities and backend API responses. Frontend does not persist its own storage; it displays and mutates data via the backend API.

---

## 1. Session

Logical investigation or ticket container. The user sees a list of sessions with creation time and optional name and external link; one session is current for uploads, log search, reports, and export.

| Field           | Type   | Notes                                      |
|-----------------|--------|--------------------------------------------|
| id              | string | Unique identifier (backend-generated)      |
| name            | string \| null | Optional display name                 |
| external_link   | string \| null | Optional link (e.g. Zendesk, Slack)  |
| created_at      | string | ISO 8601 datetime                          |
| updated_at      | string | ISO 8601 datetime                          |

**Validation**: Name and external_link are optional; no client-side format validation required beyond non-empty strings when present.

**State**: Sessions are created, selected (current), and updated via the UI; persistence is backend-only. Frontend may hold current session id in memory or localStorage for UX.

---

## 2. Upload result

Outcome of an archive upload for the current session: success or failure, and when successful, counts displayed to the user.

| Field            | Type   | Notes                                |
|------------------|--------|--------------------------------------|
| status           | string | e.g. `"success"` or `"failed"`       |
| files_processed  | int    | Number of files processed            |
| files_skipped    | int    | Number of files skipped              |
| lines_parsed     | int    | Lines parsed                         |
| lines_rejected   | int    | Lines rejected                       |
| session_id       | string | Session this upload belongs to       |
| error            | string \| null | Error message when status is failed |

**Validation**: Returned by backend after upload completes; frontend displays as-is. On HTTP 413/400/404, frontend shows backend `detail` as error message.

---

## 3. Log record (query result)

A single log line from a log search, with raw message and metadata.

| Field        | Type   | Notes                                    |
|--------------|--------|------------------------------------------|
| timestamp_ns | int    | Nanoseconds since epoch                  |
| raw_message  | string | Raw log line text                        |
| (labels)     | object | Optional label key-value pairs (e.g. service, environment, log_level); backend may add via extra fields |

**Validation**: Backend returns array of log records; frontend displays in a table or list. Default time range for search is full extent of session logs (backend derives when start/end omitted); user can narrow via filters.

---

## 4. Log query request

Request body for log search (session-scoped).

| Field       | Type   | Notes                                      |
|-------------|--------|--------------------------------------------|
| start       | string \| null | ISO 8601 start time; null = session min |
| end         | string \| null | ISO 8601 end time; null = session max   |
| limit       | int    | Max records to return (e.g. 1–1000)        |
| service     | string \| null | Filter by label service                |
| environment | string \| null | Filter by label environment           |
| log_level   | string \| null | Filter by label log_level              |

---

## 5. Report

Generated incident report for a session: summary, root cause, evidence, recommended fix, next steps. User can view content and export as Markdown or PDF.

| Field       | Type   | Notes                                    |
|-------------|--------|------------------------------------------|
| id          | string | Unique report identifier                 |
| session_id  | string | Owning session                           |
| created_at  | string | ISO 8601 datetime                        |
| content     | string | Report body (markdown); empty while generating |

**State**: Reports are created with empty content when generation is triggered; frontend polls GET report by id until content is non-empty, then enables view and export. Only one report generates at a time per session; trigger is disabled while one is in progress.

---

## 6. Report list item

Summary of a report in the session’s report history (no content).

| Field       | Type   |
|-------------|--------|
| id          | string |
| session_id  | string |
| created_at  | string |

---

## 7. Knowledge ingest status

Status of the global knowledge ingest (not session-scoped).

| Field        | Type   | Notes                                  |
|--------------|--------|----------------------------------------|
| status       | string | `"running"` or `"idle"`               |
| last_result  | object \| null | On idle: chunks_ingested, files_processed |
| error        | string \| null | Error message if last run failed    |

---

## 8. Knowledge search chunk

A single search result from the knowledge base.

| Field       | Type   | Notes                |
|-------------|--------|----------------------|
| content     | string | Snippet text         |
| source_path | string | e.g. file path       |
| metadata    | object | Optional extra       |

---

## 9. Exported report

Not a stored entity. When the user exports a report, the backend returns a file (Markdown or PDF) as the HTTP response body; frontend triggers a download (e.g. Content-Disposition attachment).

---

## Relationships

- **Session** has many **Upload results** (displayed as last/current result in UI).
- **Session** has many **Reports** (report history); each report has **content** that may be empty until generation completes.
- **Session** scopes **log query**: filters and time range apply to that session’s logs.
- **Knowledge** ingest and search are global (not per-session); frontend shows one ingest status and search results.
- **Metrics/dashboards**: External (Grafana); frontend only holds the URL and current session id to build the link.

---

## Frontend-only state (no backend persistence)

- **Current session id**: Which session is selected for upload, log search, reports.
- **Report poll**: When generation is in progress, frontend may poll GET report until content is present.
- **Upload in progress**: Loading state until upload response is received.
- **Optional**: Persist current session id in localStorage so it survives refresh.
