# Data Model: Upload Session State Fix

**Feature**: 010-upload-session-state-fix  
**Date**: 2026-03-15

## Scope

This feature adds or extends backend state for "has logs" and last upload result per session. Frontend state is derived from API responses and scoped by current session; no new frontend persistence entities.

## Backend Entities

### Session (existing, unchanged)

- **Session**: id, name, external_link, created_at, updated_at (existing).
- No schema change; "has logs" is derived from presence of log extent (or new upload summary row).

### Session log extent (existing)

- **session_log_extent**: session_id (PK/FK), start_ns, end_ns.
- Used to derive "has logs" (row exists ⇒ session has logs) and for log time range.
- Unchanged by this feature.

### Session upload summary (new)

Stores the last upload result per session so it can be returned after refresh.

| Field | Type | Description |
|-------|------|-------------|
| session_id | string (PK, FK → sessions) | Session this summary belongs to |
| status | string | "success" \| "partial" \| "failed" |
| files_processed | int | Count of files processed |
| files_skipped | int | Count of files skipped |
| lines_parsed | int | Count of lines parsed |
| lines_rejected | int | Count of lines rejected |
| error | string \| null | Error message when status is "failed" (or partial) |
| updated_at | datetime | When this summary was last updated |

**Relationships**:
- One-to-one with Session (one row per session, upserted on each upload).

**Lifecycle**:
- Created or updated when POST /sessions/{session_id}/logs/upload completes (success, partial, or failed).
- Read by GET /sessions/{session_id}/upload-summary.
- "Has logs" for a session can be derived from: (a) presence of session_log_extent row, or (b) presence of session_upload_summary row with status in ("success", "partial"). Prefer (a) for consistency with existing log range behavior; upload summary is for display only.

**Validation**:
- status in ("success", "partial", "failed"); counts ≥ 0; session_id must exist in sessions.

## Frontend (derived / UI state)

- **Current session id**: Already stored in localStorage; unchanged.
- **Session list with has_logs**: From GET /sessions (extended with has_logs per session) or from GET /sessions/{id}/upload-summary (200 ⇒ has logs, 404 ⇒ no summary).
- **Last upload result for current session**: From mutation (after upload) or from GET /sessions/{id}/upload-summary (on load or when selecting a session). Displayed only when result.session_id === currentSessionId.
- **Loading / error / retry**: Ephemeral UI state for the current session’s upload-summary fetch; no persistence.

## State transitions

- **On upload success/partial/failed**: Backend writes or updates session_upload_summary; updates session_log_extent on success/partial. Frontend: mutation returns result; store or display only for that session id; when switching session, display result for new session (from cache/query) or empty.
- **On page load**: Frontend fetches current session’s upload summary (and optionally has_logs for list). Show loading until done; then show summary or empty. On failure: show error + retry (retry only for selected session).
- **On session change**: Display upload result for the new current session (from query/cache or empty); if not in cache, fetch upload-summary for that session (loading, then result or empty).
