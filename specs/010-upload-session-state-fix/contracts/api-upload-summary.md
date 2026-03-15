# API Contract: Upload Summary and Has-Logs State

**Feature**: 010-upload-session-state-fix  
**Date**: 2026-03-15  
**Purpose**: New and extended endpoints so the frontend can refetch "has logs" and last upload summary per session after refresh.

---

## New endpoint

### GET `/sessions/{session_id}/upload-summary`

Returns the last upload result for the session (for display after refresh).

- **Response** `200`: Body same shape as POST `/sessions/{session_id}/logs/upload` response:
  - `status`: `"success"` | `"partial"` | `"failed"`
  - `files_processed`: number
  - `files_skipped`: number
  - `lines_parsed`: number
  - `lines_rejected`: number
  - `session_id`: string
  - `error`: string | null
- **Response** `404`: Session not found, or session has never had an upload (no summary stored).

Frontend use: Call when app loads (for current session) and when user selects a session, to show last upload summary or empty. Enables loading state, error + retry (for this session only), and success feedback per spec.

---

## Optional extension (session list)

### GET `/sessions` (extended)

- **Response** `200`: `{ "sessions": [ { "id", "name", "external_link", "created_at", "updated_at", "has_logs": boolean } ] }`
- `has_logs`: true if the session has log data (e.g. has a row in session_log_extent). Allows list UI to show which sessions have logs without calling upload-summary for each.

Implementation may defer `has_logs` on the list and derive "has logs" for the current session from GET upload-summary (200 ⇒ has logs, 404 ⇒ no summary). Contract above is the target; minimal implementation can add only GET upload-summary first.

---

## Existing behavior (unchanged)

- **POST** `/sessions/{session_id}/logs/upload`: After successful handling, backend must persist the returned result as the session’s last upload summary (upsert) so GET upload-summary can return it.
- **GET** `/sessions/{session_id}/logs/range`: Still returns 404 when no logs; frontend can use this to infer "has logs" (200 vs 404) if upload-summary is not yet implemented, but GET upload-summary is the preferred source for both "has logs" and the summary payload.
