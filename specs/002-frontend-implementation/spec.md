# Feature Specification: Log Investigation Frontend

**Feature Branch**: `002-frontend-implementation`  
**Created**: 2026-03-14  
**Status**: Draft  
**Input**: User description: "implement the frontend for this project"

## Clarifications

### Session 2026-03-14

- Q: When the user switches session during an upload or report generation, should the operation complete in the original session, be cancelled, block switching, or warn and let user choose? → A: Operation completes in the session it was started in; switching session does not cancel it. Result is tied to that session when user returns.
- Q: How should metrics/dashboards be presented (embedded in-app vs link)? → A: Link only; open session-scoped metrics/dashboards in a new tab/window (e.g. link to Grafana with session context).
- Q: Default log search time range when user has not set filters? → A: Use the full extent of ingested logs in the current session (min to max timestamp); user can narrow to a sub-range.
- Q: Is basic accessibility in scope for the frontend MVP? → A: Yes: keyboard navigation and focus order for main flows; meaningful labels for screen readers where practical; no formal audit or WCAG level claim for MVP.
- Q: Can the user start a second report for the same session while one is already generating? → A: No: one report at a time per session; while a report is generating, the user cannot start another and must wait (or cancel, if supported) before starting a new one.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Session Management (Priority: P1)

As an engineer, I want to create and switch between investigation sessions (e.g. one per support ticket) so that I can keep log data and reports separate per ticket. I want to give a session an optional name or label and an optional link to an external ticket (e.g. Zendesk, Slack), and see my session list with creation time and those details so I can return to the right investigation.

**Why this priority**: Every other feature is scoped to a session; without session management the user cannot organize work or use upload, reports, or export correctly.

**Independent Test**: Can be fully tested by creating multiple sessions with names and links, listing them, selecting one as current, and confirming the list shows creation time and optional name/link. Delivers value as a standalone way to organize investigations.

**Acceptance Scenarios**:

1. **Given** the application is open, **When** the user views the session list, **Then** they see all sessions with at least creation time and, if set, name and external link; one session is clearly indicated as current or selected.
2. **Given** the session list, **When** the user creates a new session (with optional name and optional external link), **Then** the new session appears in the list and can be selected as current; name and link are stored and shown.
3. **Given** multiple sessions, **When** the user selects a session, **Then** that session becomes the current context for uploads, log queries, and report generation; the interface clearly indicates which session is active.
4. **Given** a session is selected, **When** the user edits the session’s optional name or external link, **Then** the updated values are saved and shown in the list and session detail.

---

### User Story 2 - Log Upload and Upload Results (Priority: P2)

As an engineer, I want to upload a compressed log archive for the current session and immediately see whether it succeeded and how many files were processed, how many lines were parsed or rejected, and how many files were skipped, so I can confirm ingestion without using external tools.

**Why this priority**: Upload is the primary way to get data into the platform; visible feedback is essential for trust and troubleshooting.

**Independent Test**: Can be fully tested by selecting a session, uploading a valid archive, and verifying the interface shows success and a summary (e.g. files processed, lines parsed/rejected, files skipped). Delivers value as a standalone upload-and-verify flow.

**Acceptance Scenarios**:

1. **Given** a session is selected, **When** the user chooses a compressed archive (e.g. zip) and starts upload, **Then** the interface shows upload progress or loading state and then displays a clear result: success or failure, and on success a summary (files processed, files skipped, lines parsed, lines rejected).
2. **Given** the user uploads an archive that exceeds the documented size limit or is invalid, **When** the upload completes, **Then** the interface shows a clear error message and does not indicate success; existing data is unchanged.
3. **Given** an upload in progress, **When** the user waits for completion, **Then** they can distinguish “uploading” from “processing” if the backend supports it, or see a single clear “upload complete” outcome; errors (e.g. network, server) are shown in plain language.

---

### User Story 3 - Log Search and Inspection (Priority: P3)

As an engineer, I want to search and filter logs for the current session by labels (e.g. service, environment, log level) and time range, and view the matching log lines with their raw message and metadata, so I can investigate evidence without leaving the application.

**Why this priority**: Log search is the main way to inspect ingested data; without it the user must rely on external tools.

**Independent Test**: Can be fully tested by selecting a session with ingested logs, applying filters (e.g. service, time range), running a search, and verifying that matching log lines are shown with message and relevant metadata. Delivers value as a standalone log exploration experience.

**Acceptance Scenarios**:

1. **Given** a session with ingested logs, **When** the user sets filters (e.g. service, environment, log level, time range) and runs a search, **Then** the interface displays matching log lines with raw message content and metadata (e.g. timestamp, level, service) in a readable form (e.g. table or list).
2. **Given** search results, **When** the result set is large, **Then** the user can navigate results in a manageable way (e.g. pagination or limited window) and understand approximate count or “load more” where applicable.
3. **Given** no filters or broad filters, **When** the user runs a search, **Then** the interface uses the full extent of ingested logs in the current session (min to max timestamp) as the default time range, and the user can narrow to a sub-range; empty results show a clear “no logs match” message.

---

### User Story 4 - Metrics and Dashboards Access (Priority: P4)

As an engineer, I want to open a link to session-scoped metrics or dashboards (e.g. Grafana in a new tab) so I can view error rate, request volume, and log volume for the current session and correlate trends with log search and reports without manual configuration.

**Why this priority**: Metrics and dashboards add observability value; the frontend should make them reachable in one or two actions.

**Independent Test**: Can be fully tested by selecting a session with data, following the link to metrics/dashboards (new tab/window with session context), and confirming that the opened view is scoped to the current session. Delivers value as a standalone way to see session-scoped metrics.

**Acceptance Scenarios**:

1. **Given** a session is selected and has derived metrics, **When** the user follows the link to metrics or dashboards (opened in a new tab/window with session context, e.g. Grafana), **Then** they see session-scoped metrics (e.g. error rate, request volume, log volume) for that session.
2. **Given** the user has opened the metrics/dashboard link for the current session, **When** they switch to another session in the app, **Then** the interface clearly indicates how to open metrics for the newly selected session (e.g. a new link or the same link with updated session context).
3. **Given** no metrics are available for the session (e.g. no data yet), **When** the user uses the metrics/dashboard link or control, **Then** they see a clear message rather than an empty or broken view, or the link opens the external dashboard with clear empty-state guidance there.

---

### User Story 5 - Knowledge Base Ingest and Search (Priority: P5)

As an engineer, I want to trigger knowledge base ingestion (or re-ingestion) and see whether it is in progress or complete, and I want to run a search and see matching documentation or code snippets with source references so I can use that context for investigations.

**Why this priority**: Knowledge base supports report generation; the frontend should expose ingest and search so users can refresh the index and verify content.

**Independent Test**: Can be fully tested by triggering ingest, checking status, then running a search and verifying that results show snippets and source references. Delivers value as a standalone knowledge management and search experience.

**Acceptance Scenarios**:

1. **Given** the application is open, **When** the user starts knowledge ingestion, **Then** the interface shows that ingest is in progress and, when complete, shows a clear success or failure status; on failure, a brief reason is shown if available.
2. **Given** ingestion is complete (or already done), **When** the user runs a knowledge search query, **Then** the interface displays matching chunks with snippet content and source metadata (e.g. file path, document type) in a readable form.
3. **Given** the knowledge base is empty or ingest has not been run, **When** the user runs a search or opens the knowledge area, **Then** they see a clear message that no knowledge is available or that they should run ingestion first.

---

### User Story 6 - Report Generation, Viewing, and Export (Priority: P6)

As an engineer, I want to ask an incident question (e.g. “Why did the service fail?”) and trigger report generation for the current session, see when the report is ready and view its content (summary, root cause, evidence, recommended fix, next steps), and export that report as Markdown or PDF to attach to a ticket or share.

**Why this priority**: Report generation and export are the main outcome of the platform; the frontend must make them easy to trigger and complete.

**Independent Test**: Can be fully tested by selecting a session with logs (and optionally knowledge), triggering report generation with a question, waiting until the report has content, viewing the report in the interface, and exporting it in chosen format. Delivers value as a single end-to-end report flow.

**Acceptance Scenarios**:

1. **Given** a session is selected, **When** the user enters an incident question and triggers report generation, **Then** the interface shows that generation has started and shows progress or “in progress” until the report has content; then the user can open and read the full report (summary, root cause, evidence, recommended fix, next steps).
2. **Given** a session with one or more reports, **When** the user views that session, **Then** they can see report history (e.g. list with timestamps or titles) and open any report to view its content.
3. **Given** a report with content, **When** the user chooses to export, **Then** they can select the report (if multiple) and the format (Markdown or PDF) and receive a file download with that report’s content in the chosen format.
4. **Given** report generation is still in progress, **When** the user attempts export or views the report, **Then** the interface indicates that the report is not ready yet (e.g. “generating…” or “content pending”) and does not offer export until content is available, or clearly explains that export will be available when ready.
5. **Given** a report is already generating for the current session, **When** the user tries to start another report, **Then** the interface does not start a new generation (e.g. trigger is disabled or shows "wait for current report"); the user must wait for the current report to complete, or cancel it if that is supported, before starting a new one.

---

### Edge Cases

- When the session has no ingested logs, the default time range for log search is empty; the interface shows an empty or “no data” state and does not run a query until the user has uploaded logs or the session has data.
- What happens when the user has no sessions yet? The interface allows creating a first session and makes that session current so upload and other actions are possible.
- What happens when the user selects a session that has no uploaded logs? Log search shows an empty or “no data” state; report generation can still be triggered but the report may state limited evidence.
- What happens when the backend is unavailable (e.g. network error, server down)? The interface shows a clear, user-friendly error and does not imply success; retry or “check connection” guidance may be shown.
- What happens when an upload fails (e.g. file too large, invalid archive)? The user sees a specific error message (e.g. “Archive exceeds size limit” or “Invalid archive”) and can correct and retry.
- What happens when report export is requested before the report has content? The interface either disables export until ready or shows that the report is still generating and export will be available when complete.
- What happens when the user tries to start a second report while one is already generating? The interface does not start another; the user must wait for the current report to complete (or cancel it if supported) before starting a new one.
- What happens when the user switches session during an upload or report generation? The operation continues in the session it was started in and is not cancelled; the result (upload summary or report) is associated with that original session. The user may switch away and return later to see the result; the interface communicates this behavior (e.g. progress or result remains in context of the session where the operation was started).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The interface MUST allow users to list all sessions with at least creation time and, when set, optional name and external link; one session MUST be identifiable as the current or selected session for all session-scoped actions.
- **FR-002**: The interface MUST allow users to create a new session with optional name and optional external link; the new session MUST appear in the list and MUST be selectable as current.
- **FR-003**: The interface MUST allow users to select a session as current and to update the selected session’s optional name and external link; changes MUST be persisted and reflected in the list and session detail.
- **FR-004**: The interface MUST allow users to upload a compressed log archive (e.g. zip) for the current session and MUST display the outcome: success or failure, and on success a summary (e.g. files processed, files skipped, lines parsed, lines rejected); on failure, a clear error message MUST be shown.
- **FR-005**: The interface MUST allow users to search logs for the current session by at least time range and key labels (e.g. service, environment, log level) and MUST display matching log lines with raw message and relevant metadata in a readable form; the default time range for search MUST be the full extent of ingested logs in the current session (min to max timestamp), with the option for the user to narrow to a sub-range; large result sets MUST be presented in a manageable way (e.g. pagination or limited window with clear indication of more).
- **FR-006**: The interface MUST provide a link that opens session-scoped metrics or dashboards in a new tab or window (e.g. link to Grafana) with session context so users can view metrics (e.g. error rate, request volume, log volume) for the current session; when the user switches session, the interface MUST clearly indicate how to open metrics for the newly selected session (e.g. link updates with session context or user opens link again for the new session).
- **FR-007**: The interface MUST allow users to trigger knowledge base ingestion and MUST show ingest status (in progress, complete, or failed with brief reason if available); it MUST allow users to run a knowledge search and display results with snippet content and source metadata (e.g. file path, document type).
- **FR-008**: The interface MUST allow users to trigger report generation for the current session by providing an incident question; it MUST show that generation has started and progress or “in progress” until the report has content, then MUST allow the user to view the full report (summary, root cause, evidence, recommended fix, next steps). Only one report MUST be generating at a time per session; while generation is in progress, the interface MUST NOT allow starting another report (e.g. trigger disabled or “wait for current report”); the user may cancel the in-progress generation if that capability is supported.
- **FR-009**: The interface MUST show report history for the current session (e.g. list of reports with timestamps or identifiers) and MUST allow the user to open any report to view its content.
- **FR-010**: The interface MUST allow users to export a chosen report (from report history) in Markdown or PDF format and MUST provide the exported file as a download; export MUST only be offered or succeed when the report has content, with clear feedback when the report is still generating.
- **FR-011**: The interface MUST display errors (network, server, validation) in clear, user-friendly language and MUST not indicate success when an operation has failed; where applicable, it MUST support retry or recovery guidance.
- **FR-012**: When the user switches to another session while an upload or report generation is in progress, the operation MUST continue in the session it was started in; the result MUST be visible in that original session when the user returns to it. The interface MUST NOT cancel the operation on session switch and MUST make this behavior clear (e.g. progress or result shown in the context of the session where the operation was started).
- **FR-013**: The interface MUST support keyboard navigation and logical focus order for main flows (session list and selection, upload, log search, report trigger and view, export). Interactive elements MUST have meaningful labels or text so screen readers can identify them where practical. The MVP does not require a formal accessibility audit or a specific WCAG conformance level.

### Key Entities

- **Session**: A logical investigation or ticket container. The user sees a list of sessions with creation time and optional name and external link; one session is current for uploads, log search, reports, and export. Sessions are created, selected, and updated via the interface; data is persisted by the backend.
- **Upload result**: The outcome of an archive upload: success or failure, and when successful, counts (files processed, files skipped, lines parsed, lines rejected) displayed to the user after upload completes.
- **Log result set**: The set of log lines matching the user’s search (filters and time range); each line is shown with raw message and metadata (e.g. timestamp, level, service) for inspection.
- **Report**: A generated incident report with summary, root cause, evidence, recommended fix, and next steps. The user can view report content in the interface and see report history per session; reports are identified (e.g. by timestamp or id) for selection and export.
- **Exported report**: A file (Markdown or PDF) containing one report’s content, produced when the user chooses export and selects report and format; delivered as a download.

## Assumptions

- The backend and its APIs (sessions, upload, logs query, knowledge ingest/search, reports generate/list/export) exist and are available at a configured base URL; the frontend consumes these capabilities and does not replace them.
- The product is used in a single-user or local-first context for the initial release; authentication and multi-tenant behavior are out of scope unless otherwise specified.
- Metrics and dashboards are provided by an external system (e.g. Grafana); the frontend provides a link that opens them in a new tab/window with session context so the user can reach session-scoped metrics in one or two actions.
- Archive size limits and log file patterns match the backend documentation (e.g. 500 MB uncompressed, 100 MB compressed; documented file patterns); the interface may surface these limits in upload UI or errors.
- Report generation is asynchronous; the interface will poll or otherwise reflect status until report content is available, then enable viewing and export.
- Basic accessibility is in scope for MVP: keyboard navigation, focus order, and meaningful labels for screen readers on main flows; no formal WCAG audit or conformance claim is required for the initial release.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can create a session, give it a name and optional external link, and see it in the session list with creation time and those details, and select it as current, in under one minute.
- **SC-002**: A user can upload a log archive for the current session and see a clear success or failure result with summary (files processed, lines parsed/rejected, files skipped) without using external tools.
- **SC-003**: A user can run a log search for the current session with filters and time range and view matching log lines with message and metadata in the interface.
- **SC-004**: A user can open session-scoped metrics or dashboards via a link (new tab/window with session context) from the interface in one or two actions and see data for the current session.
- **SC-005**: A user can trigger knowledge ingestion, see status, run a knowledge search, and view results with snippets and source references in the interface.
- **SC-006**: A user can trigger report generation with an incident question, see when the report is ready, view the full report in the interface, and export it as Markdown or PDF in under three minutes from trigger to download (assuming backend completes generation in a typical time).
- **SC-007**: When any operation fails (upload, search, ingest, report, export), the user sees a clear error message and no false success; retry or next-step guidance is available where applicable.
