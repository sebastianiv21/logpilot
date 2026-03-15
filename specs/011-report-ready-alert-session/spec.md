# Feature Specification: Report-Ready Alert Shows Session Context and Go-to-Session Action

**Feature Branch**: `011-report-ready-alert-session`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "When a report is ready, it also should include either the name or the session ID in the alert. Also, it should have a button to redirect to the session where it is generated."

## Clarifications

### Session 2026-03-15

- Q: Should the redirect control take the user only to the session (user then opens the report from the list), or directly to the report view when possible? → A: Session and auto-open report — select the session and open the report that just became ready so the user sees it immediately.
- Q: Preferred copy for the redirect control (e.g. "Open session", "View report")? → A: "View report".
- Q: Should the spec require the new control to be keyboard-focusable and screen-reader announced? → A: Yes, require — the control MUST be keyboard-focusable and have an accessible name (e.g. aria-label) so screen reader users get the same action.
- Q: When session name cannot be resolved (e.g. network error), is showing only session ID acceptable? → A: Yes, explicit fallback — when the session name cannot be resolved, the alert MUST show a session identifier (e.g. full or truncated session ID); document in spec.
- Q: Should the spec state that toast duration, position, and sound are unchanged? → A: Yes, add out-of-scope — spec states that toast duration, position, and sound behavior are unchanged by this feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Report-Ready Alert Includes Session Identity (Priority: P1)

When a report finishes generating, the user sees a success alert that always identifies which session the report belongs to—either by session name (when available) or by session ID—so they know which report is ready even when they have multiple sessions or are viewing another part of the app.

**Why this priority**: Without session context, a generic "Report ready" message is ambiguous when the user has multiple sessions or triggered generation in the background. Identifying the session is the core value of the feature.

**Independent Test**: Can be fully tested by generating a report (single or multiple sessions), confirming the alert text includes the session name or a short session identifier, and delivers immediate clarity about which report became ready.

**Acceptance Scenarios**:

1. **Given** the user has one or more sessions and a report has just become ready for a specific session, **When** the report-ready alert is shown, **Then** the alert message includes either that session’s display name (if set) or a concise session identifier (e.g. truncated ID) so the user can tell which report is ready.
2. **Given** a session has no custom name, **When** the report-ready alert is shown for that session, **Then** the alert shows a session identifier (e.g. session ID or shortened form) so the session is still identifiable.

---

### User Story 2 - One-Click Redirect to the Session from the Alert (Priority: P2)

When the user sees the report-ready alert, they can use a single action (e.g. a button) in or alongside the alert to navigate to the session and open the report that just became ready, so they see the report immediately without manually finding the session or the report in the UI.

**Why this priority**: Session context (P1) is necessary first; the action to go to the session multiplies the value by reducing steps to view the report.

**Independent Test**: Can be fully tested by triggering a report to become ready, then using the provided control to navigate; the app shows the session and opens that report so the user sees it immediately.

**Acceptance Scenarios**:

1. **Given** the report-ready alert is visible, **When** the user activates the "View report" control, **Then** the application navigates to the session and opens the report that just became ready so the user sees it immediately.
2. **Given** the user is already viewing that session (and optionally that report), **When** they activate the same control, **Then** the application brings the report into view or keeps it in view without confusing navigation.
3. **Given** the report-ready alert is visible, **When** the user uses the keyboard to focus and activate the "View report" control (or uses a screen reader to discover and activate it), **Then** the same navigation and report open occurs as with pointer activation.

---

### Edge Cases

- **Multiple reports become ready in quick succession**: Each alert should identify its session and offer a redirect; activating redirect for one report should take the user to that report’s session.
- **Session name is very long**: The alert should present the session identity in a way that remains readable (e.g. truncation with full value available on hover or in the redirect target).
- **User has sound disabled or is not focused on the app**: Existing behavior (toast still shown, sound best-effort) remains; the new requirements apply to the alert content and the redirect control only.
- **Session or report was removed or inaccessible after the alert is shown**: If the user activates the redirect after the session or report is no longer available, the system should handle this gracefully (e.g. show a clear message or fallback) rather than failing silently.
- **Session name cannot be loaded when building the alert**: If the session name cannot be resolved (e.g. network error), the alert MUST still show a session identifier (e.g. full or truncated session ID) so the user knows which report is ready; the "View report" control continues to work using the known session and report identifiers.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When a report transitions to ready, the report-ready alert MUST include in its message either the session’s display name (when available and non-empty) or a concise session identifier (e.g. session ID or abbreviated form) so the user can identify which session the report belongs to. When the session name cannot be resolved (e.g. network error or session unavailable), the alert MUST show a session identifier (e.g. full or truncated session ID) so the session remains identifiable.
- **FR-002**: The report-ready alert MUST offer a single, clear control labeled "View report" (e.g. button or link) that, when activated, redirects the user to the session and opens the report that just became ready.
- **FR-003**: After the user activates the redirect control, the application MUST show the target session and open that report so the user sees it immediately; if the session or report is no longer available, the system MUST indicate that clearly instead of navigating to an invalid state.
- **FR-004**: Session identity in the alert MUST be readable and, when space is limited, MAY be truncated with a way to see the full identity (e.g. tooltip) or by navigating to the session.
- **FR-005**: The "View report" control MUST be keyboard-focusable and MUST have an accessible name (e.g. aria-label) so screen reader and keyboard users can activate it the same way as pointer users.

### Out of scope

- Toast duration, position, and sound behavior are unchanged by this feature; only the alert message content and the "View report" control are in scope.

### Assumptions

- A report-ready notification (e.g. toast and optional sound) already exists when a report becomes ready; this feature extends that notification with session identity and a redirect action.
- Sessions and reports are already modeled elsewhere; this spec only defines how the alert presents session information and how the user reaches the session.

### Key Entities

- **Session**: Represents an investigation session; has an identifier and an optional display name. The alert must show one or the other so the user knows which session’s report is ready.
- **Report**: Generated for a session; when it becomes ready, the alert is shown and must reference that session and allow navigation to it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every report-ready alert clearly identifies the owning session (by name or ID) so users can tell which report is ready without opening the app elsewhere.
- **SC-002**: Users can reach the session and see the ready report in one action from the alert (e.g. one click) in 100% of cases when the session and report are still available.
- **SC-003**: When the redirect target is no longer available, users receive a clear indication instead of a broken or blank view.
- **SC-004**: Users with multiple sessions or background report generation can correctly associate each "report ready" notification with the right session and open it without extra searching.
- **SC-005**: Keyboard and screen reader users can focus and activate the "View report" control and achieve the same outcome as pointer users.
