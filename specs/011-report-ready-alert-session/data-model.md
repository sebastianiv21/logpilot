# Data Model: Report-Ready Alert Session Context and View Report

**Branch**: `011-report-ready-alert-session`  
**Date**: 2026-03-15  

This feature does not introduce new persisted entities. It extends UI behavior using existing Session and Report and adds a transient in-memory intent for “open this report.”

## Existing entities (unchanged)

- **Session**: Identifier (`id`), optional display `name`. Already used by session list and report generation. The report-ready toast displays either session name (when available) or a short session identifier (e.g. `id.slice(0, 8)`).
- **Report**: Identifier (`id`), `session_id`, `content`, `created_at`. Already used by report list and report view. The “View report” action targets a specific `(sessionId, reportId)`.

## In-app state (transient)

- **Report-to-open intent**: Optional `{ sessionId: string, reportId: string }` held in frontend state (e.g. context). When the user clicks "View report" in the toast, the app sets current session to `sessionId` and sets this intent. When the report list for that session is shown and the report is in the list, the app opens that report in the modal and clears the intent. Not persisted; not sent to the backend.

## Validation rules (from spec)

- Session identity in the toast: MUST be the session’s display name when available and non-empty; otherwise a concise session identifier (e.g. full or truncated session ID). When the session name cannot be resolved (e.g. network error), MUST show at least a session identifier (e.g. truncated ID).
- The “View report” action always targets the same `(sessionId, reportId)` that just became ready; no user input to validate beyond that.

## State transitions

1. Report transitions to ready → `notifyReportReady(sessionId, reportId, …)` runs with the same `(sessionId, reportId)`.
2. User clicks "View report" → set `currentSessionId = sessionId`, set report-to-open intent to `{ sessionId, reportId }`, navigate to `/` if needed.
3. ReportList (for current session) mounts or updates with reports → if report-to-open matches current session and `reportId` is in the reports list, set selected report to that report (open modal) and clear report-to-open intent.
4. If session or report is missing when following the intent → show a clear message (e.g. toast or inline) and clear intent; do not navigate to an invalid state.
