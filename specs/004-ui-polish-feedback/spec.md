# Feature Specification: UI polish — icons, copy, loading cues, and report-ready feedback

**Feature Branch**: `004-ui-polish-feedback`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "We installed Lucid React icons. Try to use them whenever you consider appropriate. Don't blow the platform with icons, just when appropriate. Also look for the texts in the platform and improve and simplify them. I'd also like people to give more visual cues on loading states. When a report is ready, a toast should appear and a subtle sound should play. Use the required skills for the job."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clear visual feedback when content is loading (Priority: P1)

A user performs an action that takes time (e.g. loading sessions, loading a report, uploading logs, running knowledge ingest, or generating a report). They see clear visual cues that work is in progress—not only text like "Loading…"—so they understand the system is busy and can wait confidently.

**Why this priority**: Loading states reduce confusion and perceived wait time; they are the most visible UX improvement.

**Independent Test**: Trigger any async operation (e.g. open app to load sessions, open a report, or start report generation). Confirm that loading is indicated with visible cues (e.g. spinners, skeletons, or other non-text indicators) in addition to or instead of plain text.

**Acceptance Scenarios**:

1. **Given** the user is on a screen that fetches data, **When** data is loading, **Then** the user sees a clear visual loading indicator (e.g. spinner, skeleton, or progress cue) in addition to or replacing generic "Loading…" text where appropriate.
2. **Given** the user has started an action that takes time (upload, ingest, generate report), **When** the action is in progress, **Then** the user sees a visible busy state (e.g. spinner or progress cue) and understands the system is working.

---

### User Story 2 - Notification and sound when a report is ready (Priority: P1)

A user has started report generation (possibly in the background or in another session). When the report content becomes available, they are notified by a toast message and a subtle sound so they can switch to the report without constantly checking.

**Why this priority**: Report generation can take minutes; users need to be notified when it completes so they can return to the report.

**Independent Test**: Start a report generation, optionally switch session or tab. When the report content is ready, a toast appears and a short, subtle sound plays. User can rely on this instead of polling the UI.

**Acceptance Scenarios**:

1. **Given** a report is generating (content not yet available), **When** the report content becomes available (e.g. detected by polling), **Then** a toast notification is shown (e.g. "Report ready") and a subtle sound is played once.
2. **Given** the user has multiple reports generating in different sessions, **When** any one report becomes ready, **Then** the user is notified for that report (toast and sound) so they know which report is ready.

---

### User Story 3 - Consistent, appropriate use of icons (Priority: P2)

A user navigates the platform and sees icons used consistently to reinforce meaning (e.g. sessions, reports, upload, search, export) without the interface feeling cluttered. Icons are used where they add clarity, not everywhere.

**Why this priority**: Icons improve scannability and recognition; overuse causes noise.

**Independent Test**: Browse main areas (sessions list, reports, log search, knowledge search, upload, report generate). Verify that key actions and sections have appropriate icons where they aid recognition, and that the overall density of icons is moderate.

**Acceptance Scenarios**:

1. **Given** the user is on any main screen, **When** they look at primary actions or section headings, **Then** icons appear where they meaningfully support recognition (e.g. upload, export, generate, search) and are not overused (e.g. do not add an icon to every form label or every table header; prefer primary actions and section headings).
2. **Given** the design uses an icon set (e.g. Lucid React icons), **When** icons are used, **Then** they are consistent in style and size and used only when they add value.

---

### User Story 4 - Clearer, simpler platform copy (Priority: P2)

A user reads labels, buttons, messages, and descriptions across the platform. The text is concise, consistent, and easy to understand—no jargon or long sentences where short ones suffice.

**Why this priority**: Good copy reduces cognitive load and supports accessibility; it can be done in parallel with visual changes.

**Independent Test**: Review all user-facing strings (headings, buttons, placeholders, toasts, errors, empty states). Confirm that wording is simplified and consistent, and that instructions are clear.

**Acceptance Scenarios**:

1. **Given** the user sees any heading, button, or label, **When** they read it, **Then** the text is concise and clear (e.g. "Generate report" not "Generate a new report from your question" where the shorter form is sufficient).
2. **Given** the user encounters an error or empty state, **When** they read the message, **Then** the message is helpful and non-technical where possible (e.g. "Check your connection" instead of "Backend unavailable" where the former is clearer).
3. **Given** the user sees loading or status text, **When** they read it, **Then** the wording is consistent (e.g. "Loading…" vs "Loading report…" used deliberately) and simplified.

---

### Edge Cases

- If the user has disabled or muted browser sound, the report-ready notification still shows the toast; sound is best-effort and must not be required for accessibility.
- If multiple reports become ready in quick succession, the user receives a notification per report (toast and optionally sound) so they know each is ready; sound should be throttled or queued to avoid overlapping loud playback.
- If the user is not on the report list or report view when a report becomes ready, the toast and sound still fire so they are notified in the background.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST show clear visual loading indicators (e.g. spinner, skeleton, or progress cue) for all major async operations (sessions list, report list, report content, log search, upload, knowledge ingest, report generation) so users can see that work is in progress without relying only on text.
- **FR-002**: When a report transitions from "generating" (no content) to "ready" (content available), the system MUST show a toast notification (e.g. "Report ready") and MUST play a short, subtle sound once.
- **FR-003**: The system MUST use icons only where they add clarity—for primary actions, key sections, or status—and MUST NOT overuse icons (e.g. on every label or every button).
- **FR-004**: All user-facing text (headings, buttons, placeholders, toasts, errors, empty states, loading messages) MUST be reviewed and simplified for clarity and consistency.
- **FR-005**: The report-ready sound MUST be subtle and non-jarring (short, low volume) and MUST NOT block or replace the toast; users who cannot or do not want sound MUST still receive the toast.
- **FR-006**: Loading states MUST be visible and recognizable (e.g. via spinner, skeleton, or aria-busy) so users and assistive technologies can detect ongoing work.

### Key Entities

- Not applicable (no new data entities; changes are presentation and copy only).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify that the system is loading or busy within 2 seconds of an async action starting, without having to read fine print.
- **SC-002**: When a report becomes ready (including in the background), users are notified via toast and optional sound within the same polling cycle (e.g. within a few seconds of content availability).
- **SC-003**: Copy is shorter and clearer: average length of primary buttons and headings is reduced where verbosity added no value, and error/empty messages are understandable by non-technical users.
- **SC-004**: Icons appear on key actions and sections without cluttering the UI; a reviewer can confirm that icons are used in a consistent, purposeful way.

## Clarifications / Decisions

*(Resolved during clarification pass so the spec is unambiguous for planning.)*

- **Report-ready toast content**: The toast MUST indicate that a report is ready. When the user has multiple sessions or reports, the message MUST include enough context (e.g. session name or identifier) so the user knows which report became ready. Example: "Report ready" when only one report is generating; "Report ready (Session X)" or similar when multiple sessions exist.
- **Copy review scope (FR-004)**: "All user-facing text" means every string shown in the main application: sessions (list, create, edit), reports (list, generate, view, export), log search and results, knowledge search and ingest, upload logs, connection banner, and any modals or dialogs. Excludes debug-only or future admin-only surfaces.
- **Sound when multiple reports ready**: One toast per report is always shown. Sound MAY be played once per report; if multiple reports become ready in quick succession, sound MUST be throttled or queued so that only one sound plays at a time and playback does not overlap.

## Assumptions

- The icon library (Lucid React icons; npm package `lucide-react`) is or will be available in the frontend dependency set.
- "Subtle sound" means a short, low-volume, non-alarming tone (e.g. a single soft chime or beep) that can be implemented with the Web Audio API or a small asset; browser autoplay policies may require the first sound to follow a user gesture (e.g. after the user has started report generation).
- Existing toast infrastructure (e.g. Sonner) is used for the report-ready toast; no new notification system is required.
- Loading indicators should align with the existing design system (e.g. DaisyUI components) where possible for consistency.
