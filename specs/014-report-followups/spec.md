# Feature Specification: Report Follow-Up Improvements

**Feature Branch**: `014-report-followups`  
**Created**: 2026-03-29  
**Status**: Draft  
**Input**: User description: "Add prompt for Coding agent fix in the generated report. The report history list should include the incident questions. Add a little copy button to the generated report that's rendered in the viewport, similar to what we did for the session ID. Fix Export PDF functionality"

## Clarifications

### Session 2026-03-29

- Q: What exact representation should the new report copy control place on the clipboard? → A: Copy the report as Markdown-formatted report content.
- Q: How much of the incident questions should each report history entry show by default? → A: Show a short preview in the list and reveal the full questions on demand.
- Q: Where should the coding-agent fix prompt be visible? → A: Show the coding-agent fix prompt only inside the full generated report.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Report Includes Coding-Agent Fix Prompt (Priority: P1)

As an engineer reading a generated incident report, I want the report to include a clear coding-agent fix prompt so that I can hand off a concrete, implementation-ready next step without rewriting the report findings into a separate instruction.

**Why this priority**: The report is most valuable when it drives action. If the coding handoff is missing or inconsistent, users have to manually translate findings into an engineering prompt, which slows response and introduces ambiguity.

**Independent Test**: Can be fully tested by generating a report and verifying that the rendered report and exported versions include a distinct coding-agent fix prompt derived from the report findings.

**Acceptance Scenarios**:

1. **Given** a report is generated for an incident, **When** the user opens the report, **Then** the report ends with a dedicated coding-agent fix prompt section that tells a coding agent what to fix based on the incident findings.
2. **Given** the same report is exported, **When** the user opens the exported content, **Then** the coding-agent fix prompt is preserved as part of the full report content rather than omitted from export.
3. **Given** the report includes uncertainty or partial evidence, **When** the coding-agent fix prompt is shown, **Then** the prompt reflects the report context without overstating certainty or inventing unsupported fixes.

---

### User Story 2 - Report History Shows Incident Questions (Priority: P1)

As an engineer reviewing report history, I want each history entry to include the incident questions that shaped the report so that I can understand the investigation context and compare why reports differ across runs.

**Why this priority**: Report history without the initiating questions loses important context. Users need to know what was asked in order to interpret the generated answer and decide whether a rerun is necessary.

**Independent Test**: Can be fully tested by generating one or more reports with incident questions and confirming the report history list displays those questions alongside each history entry.

**Acceptance Scenarios**:

1. **Given** a report was generated from an incident question, **When** the user views the report history list, **Then** the corresponding history entry shows a readable preview of that incident question and allows access to the full incident question on demand.
2. **Given** multiple report history entries exist for the same session, **When** the user scans the list, **Then** they can distinguish entries based on the visible incident-question preview without opening each report first.
3. **Given** an older history entry has no stored incident questions, **When** the user views the list, **Then** the interface handles that missing context gracefully without breaking layout or mislabeling the entry.
4. **Given** the report history list is visible, **When** the user scans history entries, **Then** the list does not surface the coding-agent fix prompt there and keeps that content within the full generated report view.

---

### User Story 3 - Rendered Report Supports Quick Copy (Priority: P2)

As an engineer viewing a generated report in the app, I want a small copy control in the report viewport so that I can quickly copy the rendered report content for sharing in tickets, chats, or coding tools.

**Why this priority**: Copying the current report is a frequent follow-up action. A local viewport control reduces friction and aligns with the existing session ID copy pattern users already understand.

**Independent Test**: Can be fully tested by opening a rendered report, activating the copy control, and pasting the copied Markdown content into another surface to confirm the report content was copied successfully with its structure preserved.

**Acceptance Scenarios**:

1. **Given** a generated report is visible in the viewport, **When** the user activates the report copy control, **Then** the current report is copied successfully as Markdown-formatted content.
2. **Given** the user relies on keyboard or assistive technology, **When** they navigate to the report copy control, **Then** the control is focusable, clearly labeled, and activates the same copy behavior.
3. **Given** copying fails because clipboard access is unavailable, **When** the user activates the control, **Then** the system provides a clear failure message instead of silently doing nothing.

---

### User Story 4 - PDF Export Produces a Usable Report (Priority: P2)

As an engineer exporting a report as PDF, I want the export to complete successfully and preserve the report content in a readable document so that I can share the report outside the app without manual cleanup.

**Why this priority**: Broken PDF export blocks a core sharing workflow and undermines trust in report generation.

**Independent Test**: Can be fully tested by exporting a generated report as PDF and opening the file to confirm the export completes and the content remains readable and complete.

**Acceptance Scenarios**:

1. **Given** a generated report is available, **When** the user exports it as PDF, **Then** the export completes successfully and returns a readable PDF containing the report content.
2. **Given** the report contains multiple sections such as summary, evidence, incident questions, and coding-agent fix prompt, **When** the user opens the PDF, **Then** those sections appear in the document in a readable order.
3. **Given** PDF export cannot complete, **When** the user attempts export, **Then** the system informs the user clearly that the export failed instead of implying success.

---

### Edge Cases

- A report is generated without any incident questions recorded; the report history should still render the entry clearly and indicate that no questions are available for that run.
- Incident questions are long, numerous, or multiline; the history list should remain readable and scannable by showing a concise preview while still allowing the user to access the full question set on demand.
- A user copies the report before generation has fully completed or while content is still refreshing; the system should avoid copying partial or misleading content.
- PDF export is attempted on a long report; the exported document should remain complete and readable across pages rather than truncating key sections.
- The report contains special characters, code snippets, or formatted lists; copy and PDF export should preserve the content meaningfully enough for downstream use.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST include a dedicated coding-agent fix prompt as the final section in each generated report so the report contains an explicit handoff for a coding agent based on the incident findings.
- **FR-002**: The coding-agent fix prompt MUST remain aligned with the report’s findings, evidence, and uncertainty and MUST NOT imply unsupported certainty or omit relevant investigation context.
- **FR-003**: The system MUST preserve the coding-agent fix prompt in every user-visible representation of the report that is intended to show the full report content, including the rendered viewport report and exported report outputs.
- **FR-004**: The coding-agent fix prompt MUST appear only within the full generated report experience and its full-report exports; the report history list MUST NOT display that prompt.
- **FR-005**: The report history list MUST show the incident questions associated with each report entry when those questions are available.
- **FR-006**: Incident questions shown in the report history list MUST be presented as a short, readable preview that lets users distinguish one report run from another.
- **FR-007**: The system MUST allow the user to access the full incident question for a report history entry on demand from the history interface.
- **FR-008**: If a report history entry has no incident questions available, the system MUST handle that state gracefully without breaking the list or displaying misleading question content.
- **FR-009**: The rendered report viewport MUST provide a visible copy control for the generated report content.
- **FR-010**: The report copy control MUST copy the current report content as Markdown-formatted content suitable for pasting into external tools or documents while preserving report structure such as headings, lists, and code blocks.
- **FR-011**: The report copy control MUST be keyboard-focusable, have an accessible name, and provide clear success or failure feedback after activation.
- **FR-012**: The system MUST allow users to export the generated report as PDF successfully when report data is available.
- **FR-013**: The exported PDF MUST contain the report content in a readable structure that preserves major sections needed to understand and act on the incident.
- **FR-014**: If PDF export fails, the system MUST communicate the failure clearly to the user and MUST NOT present the export as successful.

### Key Entities

- **Generated Report**: The user-facing incident report content produced for a session. It includes investigation findings and now also includes a dedicated coding-agent fix prompt for implementation handoff.
- **Report History Entry**: A saved record of a generated report run in the session history. It includes identifying context for that run, including the incident questions when available.
- **Incident Question**: The user-provided investigation question that guided report generation for a specific run. This question provides context in the report history list.
- **Rendered Report View**: The in-app viewport presentation of the current generated report. It includes a copy control for quickly reusing the report content.
- **Exported PDF Report**: A portable document version of the generated report intended for sharing outside the application.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of newly generated reports include a visible coding-agent fix prompt in the in-app report view.
- **SC-002**: Users can distinguish report history entries by their incident questions without opening the full report in at least 90% of sampled multi-report sessions.
- **SC-003**: Users can copy the currently rendered report from the viewport in one action and paste usable Markdown content into an external destination in at least 95% of attempts where clipboard access is available.
- **SC-004**: PDF export succeeds for at least 95% of valid generated reports during acceptance testing and, when it fails, every failure is communicated clearly to the user.
- **SC-005**: Exported PDFs include the same major investigation sections users rely on in the in-app report view, including the coding-agent fix prompt, in 100% of acceptance-test exports.

## Assumptions

- The product already stores or can associate incident questions with each generated report run; this feature defines how that context is surfaced in history rather than introducing a new report-generation workflow.
- The existing report viewport already has a pattern for compact copy affordances, such as the session ID copy control, and the new report copy control should align with that interaction style.
- The report continues to be the source of truth for the investigation summary, evidence, and recommended next actions; this feature adds missing context and usability improvements without redefining the overall report structure.
- PDF export remains a user-initiated sharing action; this feature fixes reliability and output completeness rather than adding new export formats or delivery channels.

## Out of scope

- Changing the underlying investigation workflow or redefining how users ask incident questions.
- Adding new export formats beyond the existing PDF capability.
- Introducing automatic code changes or direct agent execution from the report itself; the scope is limited to including the coding-agent fix prompt as report content.
