# Research: Upload Session State Fix

**Feature**: 010-upload-session-state-fix  
**Date**: 2026-03-15

## 1. Where to persist "has logs" and last upload result (per session)

**Decision**: Persist on the backend and expose via API; frontend refetches on load and when needed.

**Rationale**:
- Single source of truth: works across tabs and devices and survives browser storage clear.
- Backend already has `session_log_extent` (so "has logs" can be derived: extent present ⇒ has logs). Adding last upload result (status, counts) alongside it keeps session-related state in one place.
- Spec requires showing last upload summary after refresh; refetch implies the backend must expose it. Storing it on the backend avoids duplicating logic and keeps one place to update on each upload.

**Alternatives considered**:
- **Frontend-only (localStorage)**: Store `lastUploadResult` and `sessionIdsWithLogs` in localStorage. Pros: no backend changes. Cons: lost on clear storage, not shared across tabs; "has logs" for sessions that received logs in another tab would be wrong unless we also add backend support for "has logs" in the session list.
- **Hybrid (has_logs from backend, last result from frontend)**: Backend could add `has_logs` to GET /sessions (from `get_log_extent`). Frontend could persist last upload result in localStorage. Cons: two sources of truth; last result still lost on clear storage and not shared across tabs.

## 2. How to expose "has logs" and last upload result from the backend

**Decision**: Add a small table (or extend existing schema) to store the last upload result per session; add GET endpoint(s) so the frontend can fetch "has logs" and last upload summary for the current session (or for the list).

**Rationale**:
- Existing `session_log_extent` already implies "has logs" (row exists). We need one more place to store the last upload payload (status, files_processed, files_skipped, lines_parsed, lines_rejected, error) and optionally updated_at.
- Options for exposure:
  - **Option A**: New table `session_upload_summary`; new endpoint `GET /sessions/{session_id}/upload-summary` (200 with body or 404 if no upload yet). Session list can optionally include `has_logs` (and optionally a pointer or inline summary) to avoid N+1 when rendering the list.
  - **Option B**: Extend `session_log_extent` with nullable columns for the summary fields; same GET endpoint idea.
- Prefer **Option A** (new table) to keep `session_log_extent` for time range only and avoid nullable bloat. Single endpoint `GET /sessions/{session_id}/upload-summary` returning 200 + last result or 404 is enough for the selected-session flow. For "which sessions have logs" in the list, either include `has_logs` (and optionally last summary) in GET /sessions response, or have the frontend call upload-summary only for the selected session and infer list state from extent (e.g. batch fetch or add has_logs to list). Simplest: add `has_logs` to each session in GET /sessions (from extent presence); call GET upload-summary only for the current session when needed.

**Alternatives considered**:
- **Single GET /sessions/{id} that includes upload_summary**: Same data, different shape; acceptable. We document the contract either way.
- **No new endpoint, only extend session list**: If we add `has_logs` and `last_upload_summary` to each session in GET /sessions, the frontend could use the list only. Cons: list payload grows; we may not want full summary for every session. So: list returns `has_logs`; detail/summary endpoint for the current session returns full last upload result.

## 3. Frontend: scoping upload result to current session

**Decision**: Store or derive "last result" keyed by session id; render only the result for `currentSessionId`; when session changes, show loading or the new session’s result (or empty).

**Rationale**:
- Current bug: `UploadLogs` uses a single `mutation.data` and does not key by session, so switching sessions still shows the previous session’s result.
- Fix: Either (a) keep mutation result keyed by session (e.g. a map sessionId → result in context or component state) and only display `resultMap[currentSessionId]`, or (b) when session changes, clear or replace the displayed result with the result for the new session (from refetch or from keyed cache). TanStack Query supports keyed queries (e.g. `useQuery(['uploadSummary', sessionId], ...)`) so we can use that for refetched summary and key mutation cache by session id or reset mutation when sessionId changes and rely on query for that session.

**Alternatives considered**:
- **Reset mutation on session change**: Simple: when `currentSessionId` changes, clear `mutation.data` and, if the new session has logs, refetch its summary. Display = mutation.data when it’s for currentSessionId, else result from query for currentSessionId. Ensures we never show another session’s result.

## 4. Loading, error, and retry behavior

**Decision**: Implement per spec: loading indicator while fetching; on failure show error message and retry control (scoped to selected session); on successful retry show loaded state + brief success message (e.g. toast).

**Rationale**: Spec clarifications (Session 2026-03-15) define these explicitly; no extra research needed. Use existing patterns (e.g. Sonner toasts, inline error + retry button) and TanStack Query’s isLoading, isError, refetch.

## Summary

| Topic | Decision |
|-------|----------|
| Persistence | Backend stores last upload result per session; frontend refetches |
| Backend shape | New table (e.g. session_upload_summary); GET /sessions/{id}/upload-summary; optional has_logs in GET /sessions |
| Frontend scope | Result keyed by session; display only current session’s result; clear or refetch on session change |
| Load / error / retry | Loading indicator; error + retry for selected session; success toast after retry |
