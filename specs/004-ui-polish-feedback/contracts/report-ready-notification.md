# Contract: Report-ready notification

**Branch**: `004-ui-polish-feedback`  
**Date**: 2026-03-15  

Defines the user-visible behavior when a report transitions from “generating” (no content) to “ready” (content available). This is a UI behavior contract, not an API.

---

## Trigger

- **When**: A report that was being tracked as “generating” (empty `content`) is observed to have non-empty `content` (e.g. by the existing polling in `ReportGenerationContext`).
- **Where**: Any time the poll runs and finds `report.content != null && report.content.trim().length > 0` for a (sessionId, reportId) currently in `generatingBySession`.

---

## Toast

- **MUST** show a success toast (e.g. Sonner `toast.success`).
- **Message**: Must indicate that a report is ready. If only one report is generating, “Report ready” is sufficient. If multiple sessions have reports generating, the message **MUST** include enough context (e.g. session name or session id) so the user knows which report became ready (e.g. “Report ready (Session X)” or “Report ready in &lt;session name&gt;”).

---

## Sound

- **MUST** play a short, subtle, non-jarring sound once per report ready.
- **MUST NOT** block or replace the toast; users who cannot or do not want sound **MUST** still receive the toast.
- If multiple reports become ready in quick succession, sound **MUST** be throttled or queued so that only one sound plays at a time and playback does not overlap.
- First play may be gated by user gesture (e.g. after the user has started report generation) to satisfy browser autoplay policies.

---

## Edge cases (from spec)

- User has sound disabled or muted → toast still shown; sound is best-effort.
- User is not on report list or report view when report becomes ready → toast and sound still fire (background notification).
- Multiple reports ready in quick succession → one toast per report; sound throttled/queued as above.
