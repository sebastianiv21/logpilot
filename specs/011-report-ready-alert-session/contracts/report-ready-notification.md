# Contract: Report-ready notification (extended)

**Branch**: `011-report-ready-alert-session`  
**Date**: 2026-03-15  
**Extends**: `specs/004-ui-polish-feedback/contracts/report-ready-notification.md` (trigger and sound unchanged)

Defines the user-visible behavior when a report transitions from “generating” to “ready”: toast message content, session identity, and “View report” action. Trigger and sound behavior remain as in 004; this contract adds requirements for message, action, and accessibility.

---

## Trigger

Unchanged from 004: when a report tracked as “generating” (empty content) is observed to have non-empty content (e.g. polling in ReportGenerationContext), the notification runs. The caller MUST pass the same `(sessionId, reportId)` that became ready so the toast can show session context and the action can target that report.

---

## Toast message

- **MUST** show a success toast (e.g. Sonner `toast.success`).
- **Message** MUST always include which session the report belongs to:
  - Prefer the session’s display name when available and non-empty (e.g. “Report ready (Session name)”).
  - Otherwise show a concise session identifier (e.g. full or truncated session ID).
  - When the session name cannot be resolved (e.g. network error), the message MUST still include a session identifier (e.g. truncated session ID). MUST NOT show only “Report ready” with no session context.
- **Out of scope**: Toast duration, position, and sound behavior are unchanged by this feature.

---

## “View report” action

- The toast MUST include a single, clear control labeled “View report” (e.g. button or link) that, when activated:
  1. Sets the current session to the session that owns the report.
  2. Opens that report (e.g. in the report list modal) so the user sees it immediately.
- If the session or report is no longer available when the user activates the control, the system MUST show a clear indication (e.g. toast or inline message) and MUST NOT navigate to a broken or blank view.
- The control MUST be keyboard-focusable and MUST have an accessible name (e.g. `aria-label`: “View report”) so screen reader and keyboard users can activate it the same way as pointer users.

---

## Sound

Unchanged from 004: play a short, subtle sound once per report ready; do not block or replace the toast; throttle/queue when multiple reports become ready in quick succession.

---

## Edge cases

- Multiple reports ready in quick succession: each toast identifies its session and has its own “View report” action targeting that report’s session and report.
- Session name very long: truncate for display with full value available on hover or after navigating.
- Session name cannot be loaded: show session identifier (e.g. truncated ID); “View report” still uses known `(sessionId, reportId)`.
- Session or report removed after toast is shown: on “View report”, show clear message and do not navigate to invalid state.
- User already viewing that session/report: activating “View report” brings the report into view or keeps it in view without confusing navigation.
