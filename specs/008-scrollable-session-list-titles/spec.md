# Feature Specification: Scrollable Session List and Dynamic Session Titles with Copy ID

**Feature Branch**: `008-scrollable-session-list-titles`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "This session list is making me scroll down the entire screen. Can it be kind of self-contained so that session list could be scrollable on itself? Also, I would like the logs and report section to have as the title the current session. It should include the name. If it doesn't have the name, then it will be named session and the first part of the ID. You can also have below the title, under the title with the session ID. That should have a little icon where you can copy the entire session ID."

## Clarifications

### Session 2026-03-15

- Q: How many characters should "first part of the session ID" use for the section title when the session has no name? → A: Match existing UI — use the same prefix length as already shown in the session list/sidebar.
- Q: When there is no current session, what should the Logs & metrics and Reports sections show? → A: Show placeholder title (e.g. "No session selected") in both sections; hide session ID line and copy icon until a session is selected.
- Q: How should a very long session name be displayed in the section title? → A: Truncate with ellipsis; show full name on hover (e.g. tooltip).
- Q: If copying the session ID fails (e.g. clipboard permission denied), what should the user see? → A: Show failure feedback (e.g. "Copy failed" or "Couldn't copy") using the same channel as success (tooltip or toast).
- Q: Should the copy control have an accessible name for screen readers? → A: Yes — the copy control MUST have an accessible name (e.g. "Copy session ID") for screen readers.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Self-Contained Scrollable Session List (Priority: P1)

A user views the Sessions sidebar when there are many sessions. The session list is contained within its own area and scrolls independently within that area, so scrolling the list does not scroll the rest of the page (e.g. Upload logs, Logs & metrics, Reports). The rest of the layout remains stable.

**Why this priority**: Prevents the entire screen from scrolling when browsing sessions; improves usability when the session list is long.

**Independent Test**: Can be fully tested by opening the main view with enough sessions to overflow the list area, scrolling within the session list, and verifying that only the session list scrolls while the main content (upload, logs & metrics, reports) stays fixed.

**Acceptance Scenarios**:

1. **Given** the user is on the main session view with multiple sessions, **When** the session list has more items than fit in its area, **Then** the session list is displayed in a self-contained region that scrolls independently (only the list scrolls, not the whole page).
2. **Given** the session list is scrollable, **When** the user scrolls inside the session list area, **Then** the main content area (Upload logs, Logs & metrics, Reports) does not move; only the session list content scrolls.
3. **Given** the user is on the main session view, **When** the session list has few items that fit in its area, **Then** the list area does not force unnecessary scrolling and behaves consistently (no full-page scroll caused by the list).

---

### User Story 2 - Dynamic Section Titles with Current Session (Priority: P2)

A user sees the "Logs & metrics" and "Reports" sections titled with the current session’s identity. If the session has a name, that name is used as the section title. If the session has no name, the title is "Session" followed by the first part of the session ID (e.g. "Session f4bee7b1"). This makes it clear which session the content refers to.

**Why this priority**: Reduces confusion when switching sessions; users always see which session they are viewing in the main content.

**Independent Test**: Can be fully tested by selecting a session with a name and a session without a name and verifying that the Logs & metrics and Reports section titles show the session name or "Session" + first part of ID accordingly.

**Acceptance Scenarios**:

1. **Given** the current session has a name (e.g. "Incident #123"), **When** the user views the Logs & metrics or Reports section, **Then** the section title shows that name (e.g. "Incident #123").
2. **Given** the current session has no name, **When** the user views the Logs & metrics or Reports section, **Then** the section title shows "Session" followed by the first part of the session ID (e.g. "Session f4bee7b1").
3. **Given** the user switches to another session, **When** the main content is displayed, **Then** the Logs & metrics and Reports section titles update to reflect the newly selected session’s name or "Session" + first part of ID.

---

### User Story 3 - Full Session ID with Copy (Priority: P3)

A user can see the full session ID for the current session directly under the section title in both the Logs & metrics and Reports sections. A small icon next to the session ID allows the user to copy the full session ID to the clipboard in one action.

**Why this priority**: Supports sharing, debugging, and support workflows where the full ID is needed.

**Independent Test**: Can be fully tested by opening a session, locating the session ID under the section title in Logs & metrics or Reports, clicking the copy icon, and pasting elsewhere to confirm the full ID was copied.

**Acceptance Scenarios**:

1. **Given** the user is viewing the Logs & metrics or Reports section, **When** they look below the section title, **Then** the full session ID is displayed with a small copy icon next to it.
2. **Given** the full session ID and copy icon are visible, **When** the user activates the copy control (e.g. clicks the icon), **Then** the full session ID is copied to the clipboard and the user receives clear feedback (e.g. tooltip or toast) that the copy succeeded.
3. **Given** the user has copied the session ID, **When** they paste elsewhere, **Then** the pasted value is the complete session ID (unchanged from what the system displays).

---

### Edge Cases

- What happens when there is no current session (e.g. empty state)? Both Logs & metrics and Reports show a placeholder section title (e.g. "No session selected"); the session ID line and copy icon are hidden until a session is selected.
- How does the system handle a very long session name? The section title is truncated with an ellipsis; the full session name is available on hover (e.g. tooltip). The full session ID remains available via the copy control below the title.
- What is "first part of the ID"? The same short prefix of the session ID already used in the session list/sidebar (e.g. in "Session f4bee7b1"); section titles use that same length for consistency.
- What happens when clipboard copy fails (e.g. permission denied)? The user sees failure feedback (e.g. "Copy failed" or "Couldn't copy") via the same channel as success (tooltip or toast).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The session list in the sidebar MUST be displayed in a self-contained region that scrolls independently; scrolling within the session list MUST NOT scroll the rest of the page (main content area).
- **FR-002**: The Logs & metrics section MUST display as its title the current session’s name if present; if the current session has no name, the title MUST be "Session" followed by the first part of the session ID.
- **FR-003**: The Reports section MUST display as its title the current session’s name if present; if the current session has no name, the title MUST be "Session" followed by the first part of the session ID.
- **FR-004**: When the current session changes, the Logs & metrics and Reports section titles MUST update immediately to reflect the newly selected session (name or "Session" + first part of ID).
- **FR-005**: Below the section title, both the Logs & metrics and Reports sections MUST show the full session ID for the current session.
- **FR-006**: A small copy icon MUST be provided next to the displayed full session ID; activating it MUST copy the full session ID to the clipboard. The copy control MUST have an accessible name (e.g. "Copy session ID") for screen readers.
- **FR-007**: After a successful copy, the user MUST receive clear feedback (e.g. tooltip or toast) indicating that the session ID was copied; if the copy fails (e.g. clipboard unavailable), the user MUST receive failure feedback (e.g. "Copy failed" or "Couldn't copy") via the same channel.
- **FR-008**: When there is no current session, the Logs & metrics and Reports sections MUST show a placeholder section title (e.g. "No session selected") and MUST hide the session ID line and copy icon until a session is selected.
- **FR-009**: When the session name is too long to fit in the section title, the application MUST truncate it with an ellipsis and MUST show the full name on hover (e.g. via tooltip).

### Key Entities *(include if feature involves data)*

- **Session**: Represents an investigation session; has an optional name and a unique ID. The "first part" of the ID uses the same prefix length as in the session list/sidebar; the full ID is shown under the section title and is copyable.
- **Session list (sidebar)**: The list of sessions in the sidebar; must be rendered inside a self-contained, independently scrollable container so that only the list scrolls, not the entire page.
- **Logs & metrics section / Reports section**: Main content sections whose titles and session ID line reflect the current session (name or "Session" + first part of ID, plus full ID with copy).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can scroll through a long session list without the rest of the page (Upload logs, Logs & metrics, Reports) moving; only the session list area scrolls.
- **SC-002**: Users can identify the current session at a glance from the Logs & metrics and Reports section titles (session name or "Session" + first part of ID).
- **SC-003**: Users can copy the full session ID from both the Logs & metrics and Reports sections in one action and receive clear confirmation that the copy succeeded.
- **SC-004**: When switching sessions, section titles and the displayed session ID update to match the selected session without requiring a page reload.

## Assumptions

- The session list may still use pagination or "Load more" (as in existing behavior); this feature adds a self-contained scrollable container for the list, not a change to how sessions are loaded.
- "First part of the ID" means the same prefix length already shown in the session list/sidebar; section titles (when the session has no name) use that same convention for consistency.
- The copy control is a small icon (e.g. copy/clipboard icon) placed next to the full session ID; exact placement and styling follow existing product patterns.
- Feedback for successful copy can be a brief tooltip, toast, or inline message; the implementation may choose the most appropriate pattern for the product.
