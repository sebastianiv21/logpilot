# Research: Report-Ready Alert Session Context and View Report Action

**Branch**: `011-report-ready-alert-session`  
**Date**: 2026-03-15  

## 1. Toast action button (Sonner)

**Decision**: Use Sonner’s built-in `action` option on `toast.success()` to add a "View report" button.

**Rationale**: Sonner supports `toast.success(message, { action: { label: string, onClick: () => void } })`, which renders an inline button. No custom toast component or extra library is required. The action runs in the same process, so we can call a navigation callback (set session + open report) from `onClick`.

**Alternatives considered**:
- Custom toast component with a button: more code and styling to keep consistent; rejected.
- Link-only toast (no button): spec requires a clear control; rejected.

## 2. Navigation to session + report (no new routes)

**Decision**: Do not add URL routes for `/session/:id` or `/session/:id/report/:reportId`. Use existing session selection (SessionContext) plus a small “report to open” signal so that when the user clicks "View report", we set the current session and ask the report list to open the given report in the modal.

**Rationale**: Current app uses `currentSessionId` in SessionContext and report selection is local state in ReportList (modal). Adding routes would require syncing URL with context and modal state and would expand scope. A “report to open” (e.g. `{ sessionId, reportId }` in context or a callback passed to the notification layer) keeps the change local: set current session, set “open this report when this session is shown”, navigate to `/` if needed; ReportList when it has that session and the report in the list opens the modal and clears the signal.

**Alternatives considered**:
- Add `/session/:sessionId/report/:reportId`: enables shareable links but adds routing, sync with SessionContext and modal, and more tests; deferred as out of scope.
- Global event/custom event: works but is less React-idiomatic than context or callback; rejected.

## 3. Accessibility of the toast action (keyboard + screen reader)

**Decision**: Rely on Sonner’s rendering of the action as a focusable control; ensure the action button has an explicit accessible name (e.g. `aria-label`: "View report") and is keyboard-activatable. If Sonner’s default action element does not expose focus or aria, wrap or replace the action with a proper button in a custom toast description/content where necessary.

**Rationale**: Spec FR-005 and SC-005 require the "View report" control to be keyboard-focusable and to have an accessible name. Sonner’s `action` typically renders a button; we will verify focus order and aria-label (or use a custom description with a visible button that has aria-label) so screen reader and keyboard users get the same outcome as pointer users.

**Alternatives considered**:
- Rely only on visible "View report" text: may be sufficient for some screen readers if the control is a native button; we will confirm and add aria-label if needed.
- Custom toast content with a full control: use if default action is not focusable or announced; acceptable fallback.

## 4. Session label fallback when name unavailable

**Decision**: Reuse existing pattern: `getSession(sessionId)` then `name && name.trim() ? name : id.slice(0, 8)`; on network/error use `sessionId.slice(0, 8)`. Always show at least this label in the toast message (remove the “only when generatingCount > 1” branch so every report-ready toast includes session identity).

**Rationale**: Spec FR-001 and clarification require that when the session name cannot be resolved, the alert MUST show a session identifier (e.g. truncated ID). Current `getSessionLabel` already does this in a catch; we keep it and always include its result in the message.

**Alternatives considered**:
- Show "Report ready" with no session when name fails: contradicts spec; rejected.
- Full session ID only when name fails: acceptable; truncated ID is sufficient and shorter.

## 5. Where to hold “report to open” state

**Decision**: Add a small “report to open” capability: either a new context (e.g. `ReportToOpenContext`) with `{ sessionId, reportId } | null` and `openReport(sessionId, reportId)` / `clearReportToOpen()`, or extend SessionContext with the same. When "View report" is clicked: set current session to `sessionId`, set report-to-open to `{ sessionId, reportId }`, navigate to `/` if not already there. ReportList (or a wrapper that has access to current session and report-to-open) when `currentSessionId === reportToOpen.sessionId` and reports have loaded, if the report is in the list then set selected report and clear report-to-open.

**Rationale**: ReportList owns the modal and `selectedReport` state; it cannot be driven by a callback from the toast alone because the toast is triggered from ReportGenerationContext. So we need a shared signal that ReportList can read when it renders with the matching session. A dedicated context keeps SessionContext focused on session selection and makes the “open this report” intent explicit and testable.

**Alternatives considered**:
- Extend SessionContext with `reportIdToOpen`: same behavior; acceptable if we prefer fewer contexts.
- URL query param e.g. `/?openReport=reportId`: would require session in URL too for consistency; rejected in favor of context for this feature.
