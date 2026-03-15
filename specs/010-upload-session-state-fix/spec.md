# Feature Specification: Upload State Scoped Per Session and Persistent Across Refresh

**Feature Branch**: `010-upload-session-state-fix`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "When I upload a file, and then change to another session; it's showing the same information. Also, if I refresh the page, the information disappears."

## Clarifications

### Session 2026-03-15

- Q: After refresh, for a session that has logs, should the UI show only "has logs" or also the last upload summary (counts, charts)? → A: Show last upload summary again after refresh (requires storing or refetching that result).
- Q: When determining "has logs" after refresh, what should the user see while loading? → A: Show a loading indicator (e.g. spinner or skeleton) until state is known.
- Q: If "has logs" or last upload result cannot be determined after refresh (e.g. network error), what should happen? → A: Show an error message and allow the user to retry (e.g. retry button or link).
- Q: When the user clicks retry after a failed load, what should be retried? → A: Retry only for the currently selected session's state.
- Q: After a successful retry (session state loads), what should the user see? → A: Show the loaded state plus a brief success message (e.g. toast or inline "Loaded").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload Result Shown Only for Current Session (Priority: P1)

When a user uploads a log file for a session and then switches to a different session, the upload summary (success/partial/failed message, counts, charts) must not carry over. The screen must show only the upload result for the currently selected session, or no upload result if that session has none in context.

**Why this priority**: Showing another session's upload result is confusing and can lead to wrong conclusions about the current session's data. This is the most visible bug.

**Independent Test**: Upload to session A, switch to session B; confirm the upload summary either shows B's result or is empty. Then switch back to A and confirm A's result is shown again (if still in context).

**Acceptance Scenarios**:

1. **Given** the user has just uploaded a file for session A and sees a success summary, **When** the user selects session B, **Then** the upload summary area shows only information for session B (or is empty if B has no upload in context).
2. **Given** the user is viewing session A with no upload result shown, **When** the user uploads a file for session A, **Then** the summary shown is for session A only.
3. **Given** the user has uploaded for session A and then selected session B, **When** the user selects session A again, **Then** the upload result for session A is shown again (if still in context), not B's.

---

### User Story 2 - Upload and "Has Logs" State Survives Page Refresh (Priority: P2)

After the user refreshes the page, the application must still know which sessions have logs and must be able to show the last upload summary (counts, charts) for each such session. When the user selects a session that has logs (from a previous upload in the same or an earlier visit), the application must reflect that and show the last upload result again—e.g. allow log search and display the upload summary—without requiring a new upload.

**Why this priority**: Losing "has logs" and upload context on refresh makes the product feel fragile and forces unnecessary re-uploads. Fixing it restores trust and avoids duplicate work.

**Independent Test**: Upload to a session, refresh the page, select the same session; confirm the app still treats the session as having logs (e.g. log search or relevant UI is available). No re-upload required.

**Acceptance Scenarios**:

1. **Given** the user has uploaded logs for session A, **When** the user refreshes the page and selects session A, **Then** the application indicates that session A has logs, shows the last upload summary (counts, charts), and does not require the user to upload again to use log-related features.
2. **Given** the user has refreshed the page, **When** the user selects a session that has logs from a previous upload, **Then** the correct state (e.g. "has logs") and the last upload summary are shown for that session.
3. **Given** the user has refreshed the page, **When** the user selects a session that has never had logs uploaded, **Then** the application does not show that session as having logs.

---

### Edge Cases

- While the application is determining "has logs" and last upload result after a refresh, the system MUST show a loading indicator (e.g. spinner or skeleton) for the selected session so the user does not see another session's result or an incorrect empty state.
- What happens when the user switches session while an upload is in progress? The in-progress state should remain associated with the session that started it; after completion, the result is shown only for that session when it is selected.
- What happens when the user refreshes and the backend no longer has data for a session (e.g. session or logs were removed)? The application should reflect the current backend state and not show stale "has logs" or upload result for that session.
- If the system cannot re-establish "has logs" or the last upload result after refresh (e.g. network error or service unavailable), the system MUST show an error message and MUST offer the user a way to retry (e.g. retry button or link); retry applies only to the currently selected session's state. The system MUST NOT show another session's result or assume the current session has no logs without the user retrying.
- What happens when the same session is selected again after switching away? The upload result for that session (if still in context) is shown; no cross-session leakage.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST display upload result (summary, success/partial/failed message, and any derived metrics or charts) only for the session to which that upload belongs. When the user switches to another session, the displayed result MUST be that session's result or none.
- **FR-002**: The system MUST persist or re-establish which sessions have logs and the last upload result per session so that after a full page refresh the application still reflects the correct state and can show the last upload summary (counts, charts) for each session that has logs, without requiring the user to re-upload.
- **FR-003**: When the user selects a session after a refresh, the system MUST show that session's true state (has logs or not) and, if it has logs, the last upload result (summary, counts, charts) so that log-related features behave correctly.
- **FR-004**: An upload in progress MUST be tied to the session that initiated it; after completion, the result MUST be shown only when that session is selected.
- **FR-005**: The system MUST NOT show another session's upload result when the current session selection changes.
- **FR-006**: While loading session log state or last upload result after a refresh, the system MUST show a loading indicator (e.g. spinner or skeleton) and MUST NOT show another session's result or imply the current session has no logs until loading completes.
- **FR-007**: If the system cannot determine "has logs" or the last upload result after refresh (e.g. network error), the system MUST show an error message and MUST provide a way for the user to retry (e.g. retry button or link); retry MUST apply only to the currently selected session's state. The system MUST NOT display another session's result or treat the session as having no logs without a retry. After a successful retry, the system MUST show the loaded state and a brief success message (e.g. toast or inline "Loaded").

### Key Entities

- **Session**: The currently selected log investigation session; identified by an identifier. Has an attribute indicating whether it has logs (from upload).
- **Upload result**: The outcome of an upload for a single session (status, files processed, lines parsed, etc.). Belongs to exactly one session.
- **Session log state**: Whether a given session has log data (from at least one successful upload). Must be known after refresh for correct UI and behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a user switches from one session to another, the upload summary area shows only the result for the currently selected session (or is empty for that session); no other session's result is shown.
- **SC-002**: After a full page refresh, the user can see which sessions have logs and, when selecting a session with logs, sees the correct state and the last upload summary (counts, charts) without re-uploading.
- **SC-003**: Users are never shown another session's upload result when changing sessions (zero cross-session display errors in normal use).
- **SC-004**: Users can refresh the page after uploading and continue using log-related features for the same session without uploading again.

## Assumptions

- "Session" is the existing log investigation session concept in the product; sessions are created and listed elsewhere.
- "Information" in the user description refers to the upload result (summary, counts, charts) and/or the fact that a session "has logs" for log search and related UI.
- The system already records which sessions have log data; the fix may involve the application using that information after refresh or retaining a minimal client-side hint, within existing architecture.
- The last upload result per session (summary, counts, charts) must be available after refresh—via persistence or refetch—so it can be shown again when the user selects that session. Full history of all past uploads per session is out of scope unless already supported.
