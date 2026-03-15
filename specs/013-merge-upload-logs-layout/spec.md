# Feature Specification: Merge Upload Logs with Logs & Metrics and Improve Layout

**Feature Branch**: `013-merge-upload-logs-layout`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "We can merge the upload logs and the logs and metrics section. You can also include the in latest upload summary, the name of the file that was uploaded. Let's think on ways to rearrange the layout to be better. \"Opens in a new tab; updates when you switch sessions.\" copy can be deleted."

## Clarifications

### Session 2026-03-15

- Q: Where should the uploaded file name come from when showing the summary after refresh or session switch? → A: Backend stores and returns the uploaded file name per session (API change; file name always available after refresh/switch).
- Q: Should that merged block have one visible section heading? → A: Yes; use the heading "Logs & metrics".
- Q: After the merge, should the home view use a single-column (stacked) layout or keep a two-column layout? → A: Two columns: merged "Logs & metrics" in one column, Reports in the other (current-style grid).
- Q: Should the merged "Logs & metrics" section include log search, or only the metrics link? → A: Only the metrics link; log search is out of scope for this feature.
- Q: When the latest upload summary is loading, should the merged section show a loading state for the summary area or hide it until loaded? → A: Show a loading indicator in the summary area (e.g. spinner or skeleton) while loading.
- Q: Should report generation be available before logs are uploaded for the session? → A: No; report generation must not be available until logs have been uploaded for the current session.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single Section for Upload and Logs/Metrics (Priority: P1)

Users see one combined section titled "Logs & metrics" that contains log upload (file picker, upload action, latest upload summary) and the metrics link (e.g. "Open in Grafana"). There is no separate "Upload logs" block and "Logs & metrics" block; the content is merged under this single heading. Log search is out of scope for this feature.

**Why this priority**: Reduces visual fragmentation and makes it clear that upload, search, and metrics belong to the same workflow.

**Independent Test**: Can be fully tested by opening the app, selecting a session, and confirming that upload controls and logs/metrics entry point appear in a single section with the visible heading "Logs & metrics".

**Acceptance Scenarios**:

1. **Given** a user is on the home view with a session selected, **When** they look at the main content area, **Then** they see one merged section that includes log upload (choose file, upload, latest result) and the metrics link (e.g. "Open in Grafana").
2. **Given** the merged section is present, **When** the user uploads a log file, **Then** the latest upload summary appears within that same section.
3. **Given** the merged section is present, **When** the user wants to open metrics, **Then** the control to open metrics (e.g. "Open in Grafana") is in that same section, without a separate "Logs & metrics" heading block.

---

### User Story 2 - Show Uploaded File Name in Latest Upload Summary (Priority: P1)

When a user has performed a log upload for the current session, the latest upload summary (the block that shows success/partial/failed and any stats or charts) also shows the name of the file that was uploaded.

**Why this priority**: Users can confirm which file the summary refers to, especially when switching sessions or returning later.

**Independent Test**: Can be fully tested by uploading a .zip file, then verifying that the summary area displays that file’s name (e.g. "my-logs.zip") alongside status and stats.

**Acceptance Scenarios**:

1. **Given** the user has just uploaded a file (e.g. "logs-2024.zip"), **When** the upload completes successfully, **Then** the latest upload summary shows the uploaded file name (e.g. "logs-2024.zip") together with status and any stats/charts.
2. **Given** the user has previously uploaded a file for the current session, **When** they view the latest upload summary (e.g. after refresh or switching back to the session), **Then** the summary still shows the name of the file that was uploaded when that summary was generated.
3. **Given** the upload failed, **When** the user views the summary, **Then** the failed summary may still show the file name that was attempted, where applicable.

---

### User Story 3 - Improved Layout Arrangement (Priority: P2)

The overall layout of the home view uses a two-column grid: the merged "Logs & metrics" section in one column and the Reports section in the other (session title above). Layout is rearranged so that sections are grouped for clarity and task flow with less redundancy.

**Why this priority**: Improves usability without changing functionality; supports the merge and reduces cognitive load.

**Independent Test**: Can be tested by reviewing the home view and confirming a two-column layout: one column for "Logs & metrics" (upload + summary + metrics link), the other for Reports, with coherent spacing and grouping.

**Acceptance Scenarios**:

1. **Given** the user is on the home view, **When** they scan the page, **Then** the layout presents a two-column grid: session title at top, one column for the merged "Logs & metrics" section and one for Reports, without unnecessary duplication of headings or blocks.
2. **Given** the new layout is in place, **When** the user completes common tasks (upload, open metrics, generate report), **Then** the flow between sections feels natural and does not require excessive scrolling or hunting.
3. **Given** no logs have been uploaded for the current session, **When** the user views the home view, **Then** report generation is not available (FR-008). **Given** the user has uploaded logs for the session, **When** they view the home view, **Then** report generation becomes available.

---

### User Story 4 - Remove "Opens in a new tab; updates when you switch sessions." Copy (Priority: P2)

The helper text that says "Opens in a new tab; updates when you switch sessions." (shown next to the control that opens metrics in a new tab) is removed. The control (e.g. button) remains; only this explanatory sentence is deleted.

**Why this priority**: Simplifies the UI and removes redundant copy as requested.

**Independent Test**: Can be fully tested by opening the view that contains the "Open in Grafana" (or equivalent) control and confirming that the sentence "Opens in a new tab; updates when you switch sessions." is no longer displayed anywhere.

**Acceptance Scenarios**:

1. **Given** the user is viewing the section that contains the link/button to open metrics (e.g. Grafana) in a new tab, **When** they look at the surrounding text, **Then** the phrase "Opens in a new tab; updates when you switch sessions." is not present.
2. **Given** the copy has been removed, **When** the user uses the control to open metrics, **Then** the behavior (opening in a new tab, session-specific URL) is unchanged; only the explanatory text is gone.

---

### Edge Cases

- What happens when there is no latest upload (e.g. new session)? The merged section still shows upload controls and metrics link; the "latest upload summary" area may show nothing or a neutral state, and file name is not required when there is no upload.
- What happens when the latest upload summary is loading (e.g. after session switch)? The summary area MUST show a loading indicator (e.g. spinner or skeleton) until data is available (FR-007).
- What happens when the last upload was from a different session? The summary shown is for the current session only; the backend stores and returns the last upload file name per session, so the file name displayed always matches the summary for that session.
- What happens when the layout is viewed on a narrow viewport? The two-column layout should collapse to a stacked (single-column) arrangement so that the merged "Logs & metrics" section and reports remain accessible without horizontal scroll or overlap (FR-005).
- What happens when the current session has no log upload yet? Report generation must not be available until at least one upload has been made for that session; the UI must make this clear (FR-008). After an upload exists for the session, report generation becomes available.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST present a single merged section with the visible heading "Logs & metrics" that contains log upload (file selection, upload action, latest upload summary) and the metrics link (e.g. link or button to open Grafana or equivalent). Log search is out of scope for this feature.
- **FR-002**: The latest upload summary MUST display the name of the file that was uploaded for that summary (when a file was uploaded and the summary is available).
- **FR-003**: The home view layout MUST use a two-column grid: one column for the merged "Logs & metrics" section and one for the Reports section (session title above), with sections grouped for clarity and task flow.
- **FR-004**: The product MUST remove the exact helper text "Opens in a new tab; updates when you switch sessions." from the area next to the control that opens metrics in a new tab; the control and its behavior MUST remain.
- **FR-005**: The merged section MUST remain usable on narrow viewports (e.g. single column or responsive stacking) without losing access to upload or metrics.
- **FR-006**: The system MUST store the uploaded file name per session on the server and return it with the upload summary so that the file name is available after refresh or when the user switches back to the session.
- **FR-007**: While the latest upload summary is loading (e.g. after session switch or refetch), the merged section MUST show a loading indicator in the summary area (e.g. spinner or skeleton) so users see that data is loading.
- **FR-008**: The action of generating a new report MUST NOT be available until the current session has had at least one log upload (success or partial). Until then, the product MUST make the generate-report control unavailable (e.g. disabled or hidden with clear indication); viewing the list of existing reports may remain available. After an upload exists for the session, report generation becomes available.

### Key Entities

- **Latest upload summary**: The per-session summary of the most recent log upload, including status (success/partial/failed), optional stats/charts, and the uploaded file name. The file name is persisted server-side and returned with the summary so it is available after refresh or session switch.
- **Merged upload-and-logs section**: The single UI section with the heading "Logs & metrics" that combines upload controls, latest upload summary, and the metrics link (e.g. "Open in Grafana"). Log search is not part of this section for this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can perform log upload and access logs/metrics from one clearly identifiable section without switching between two separate blocks.
- **SC-002**: Users can identify which file a latest upload summary refers to by seeing the uploaded file name in that summary.
- **SC-003**: Users complete the common flow (upload → check summary → open metrics or generate report) with fewer distinct visual sections and no redundant "Opens in a new tab; updates when you switch sessions." copy.
- **SC-004**: The home view layout is measurably simpler (e.g. fewer top-level section headings or cards) while retaining all current capabilities (upload, summary, metrics link, reports).
- **SC-005**: Users cannot access report generation until the current session has at least one log upload; once uploaded, report generation becomes available, reducing attempts to generate reports with no data.
