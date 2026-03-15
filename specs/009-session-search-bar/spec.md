# Feature Specification: Session Search Bar

**Feature Branch**: `009-session-search-bar`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "add session search bar. can search by name, session, or external link. Use the required skills for the job."

## Clarifications

### Session 2026-03-15

- Q: Should matching be case-sensitive or case-insensitive? → A: Case-insensitive.
- Q: How should whitespace-only input be treated? → A: Trim whitespace; if the trimmed value is empty, show the full list (treat as no filter).
- Q: Should this feature define accessibility requirements for the session search? → A: Yes — accessible label for the search input and live region announcing result count or "no sessions match".
- Q: Where should the session search bar appear? → A: Directly above the scrollable session list in the sidebar (same column, search then list).
- Q: When should the filtered list update relative to typing? → A: After a short pause (e.g. 150–300 ms after last keystroke).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search Sessions by Name, ID, or External Link (Priority: P1)

A user has many sessions in the session list and wants to quickly find one. They can type in a search bar; the list shows only sessions that match the search text. Matching is based on the session name, the session ID, or the session’s external link. As they type or clear the search, the list updates to show the relevant sessions.

**Why this priority**: Core value of the feature—reduces time to find a session when the list is long.

**Independent Test**: Can be fully tested by loading the app with multiple sessions, entering text in the search bar, and verifying that only sessions matching that text (in name, ID, or external link) are shown.

**Acceptance Scenarios**:

1. **Given** the user is on the main view with a session list, **When** they enter text in the session search bar, **Then** the list shows only sessions whose name, session ID, or external link contains that text (or matches according to defined matching rules).
2. **Given** the user has entered search text, **When** they clear the search input, **Then** the full session list is shown again.
3. **Given** the user has entered search text, **When** no sessions match (name, ID, or external link), **Then** the user sees a clear empty state (e.g. “No sessions match your search”) instead of an empty list with no explanation.

---

### User Story 2 - Clear Empty State When No Matches (Priority: P2)

A user runs a search that matches no sessions. They see an explicit message that no sessions match, so they know the result is due to the search filter and not a loading or data error.

**Why this priority**: Improves clarity and avoids confusion when the filtered result is empty.

**Independent Test**: Can be fully tested by entering search text that matches no session and verifying the empty-state message appears; then clearing the search and verifying the full list returns.

**Acceptance Scenarios**:

1. **Given** at least one session exists in the list, **When** the user enters search text that matches no session (by name, ID, or external link), **Then** the UI shows an empty state message indicating that no sessions match the search.
2. **Given** the user sees the “no sessions match” empty state, **When** they clear the search, **Then** the full session list is shown again.

---

### Edge Cases

- When the search input is empty or contains only whitespace (after trimming), the full session list is shown (no filter applied).
- When the user types characters that could be interpreted as special or regex-like, the system treats the input as plain text and matches in a predictable way (e.g. literal substring match).
- When sessions have no name or no external link, matching is based only on the fields that exist (e.g. ID always exists and can be matched).
- When the list is already filtered by search and the user adds more text, the list updates after a short pause (e.g. 150–300 ms) after typing stops, without requiring a separate “search” or “submit” action.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a search input (search bar) associated with the session list so users can filter sessions by text. The search bar MUST be placed directly above the scrollable session list in the sidebar (same column: search then list).
- **FR-002**: The system MUST filter the session list by matching the user’s search text against at least: session name, session ID, and external link. A session is shown if any of these fields match the search text.
- **FR-003**: Matching MUST be consistent and predictable: substring match, case-insensitive. A session matches if the search text appears in any of its searchable fields (name, ID, or external link) ignoring case.
- **FR-004**: When the search input is empty or contains only whitespace (after trimming), the system MUST show the full session list (no filter).
- **FR-005**: When one or more sessions exist but none match the current search text, the system MUST display an empty state that clearly indicates no sessions match the search (not a generic “no sessions” or loading state).
- **FR-006**: When the user clears the search input, the system MUST restore the full session list.
- **FR-007**: The session search input MUST have an accessible name (e.g. via label or aria-label) so assistive technologies can identify it. The system MUST expose the filter result to assistive technologies (e.g. via a live region) by announcing either the number of matching sessions or a "no sessions match" message when the filtered list is empty.
- **FR-008**: The filtered list MUST update after a short pause (e.g. 150–300 ms) after the user stops typing, rather than on every single keystroke.

### Key Entities

- **Session**: Represents an investigation session. Relevant attributes for search: name (optional), unique identifier (ID), and optional external link. These are the only fields used for matching in the search bar.

## Assumptions

- Matching is substring-based and case-insensitive: a session matches if the search text appears in the session name, session ID, or external link (ignoring case).
- The search bar is used to filter the session list that the user already sees (e.g. in the sidebar); it does not replace the list with a separate “search results” page.
- “Session” in “search by name, session, or external link” refers to the session identifier (ID).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can find a session by typing part of its name, ID, or external link and see the list update to show only matching sessions, without needing extra steps (e.g. submit button).
- **SC-002**: When no sessions match the search, users see a clear empty-state message so they can tell the result is from filtering, not from an error or missing data.
- **SC-003**: Users can restore the full session list by clearing the search input in one obvious action (e.g. clearing the field or a clear control).
