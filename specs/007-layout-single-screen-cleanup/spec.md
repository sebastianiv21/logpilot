# Feature Specification: Single-Screen Layout, Pagination, and Copy Cleanup

**Feature Branch**: `007-layout-single-screen-cleanup`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "there is a lot of empty space that we can use to rearrange the elements and try to have everything in a single screen without the need to scroll. The search list is unpaginated, so it's basically an infinite scroll, which is not good. Also, when I go to the knowledge space menu, the Back to Home is in the top-nav part; that shouldn't be there. That should be somewhere in the knowledge space menu. You can see there is still plenty of copy that's either repeated or there are repeated icons as well."

## Clarifications

### Session 2026-03-15

- Q: Should the application name in the top bar act as the home link? → A: Yes; LogPilot copy in the top bar should return the user to the home screen.
- Q: Should an application icon appear in the top bar? → A: Yes; add an icon (e.g. from Lucide React) representing the application, e.g. logs-related.
- Q: Should the sessions list in the sidebar be paginated in this feature? → A: Yes; paginate the sessions list (e.g. fixed page size + "Load more" or next/previous).
- Q: Which pagination pattern for sessions list and KB search? → A: Same pattern for both — "Load more" with optional "Previous" or back-to-start if needed.
- Q: How should we use space to achieve single-screen layout? → A: Take advantage of the space on the right, e.g. moving some sections to the right (use horizontal layout).
- Q: If content still doesn't fit after rearranging (including right-side space), what should we do? → A: Rearrange only; no collapsible or compact sections. If it still doesn't fit, scrolling is acceptable.
- Q: Default page/batch size for sessions list and KB search? → A: 10 items per batch (fixed; no user control).
- Q: Should upload/processing stats (files processed, lines parsed, rejected, coverage) be presented visually? → A: Yes; use a charts library to make this information more visual (any suitable library is acceptable).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single-Screen Session View (Priority: P1)

A user opens the main session view (sessions list, upload logs, logs & metrics, reports) and can see all primary sections and actions on one screen without vertical scrolling. Empty space is used to arrange content so the layout fits the viewport.

**Why this priority**: Eliminating unnecessary scrolling for the primary workflow improves task completion and reduces cognitive load.

**Independent Test**: Can be fully tested by opening the session view at a typical desktop resolution and verifying that upload, logs & metrics, and reports sections are visible and usable without scrolling.

**Acceptance Scenarios**:

1. **Given** the user is on the main session view, **When** the viewport is at a typical desktop size, **Then** the Sessions sidebar and the main content (Upload logs, Logs & metrics, Reports) fit within one screen without vertical scroll.
2. **Given** the session view is open, **When** the layout is rendered, **Then** empty space is used effectively, including space on the right (e.g. some sections moved to the right in a horizontal or multi-column arrangement) so that key actions and sections are visible at a glance.
3. **Given** the sessions list has more than one page of items, **When** the user views the sidebar, **Then** sessions are shown in pages (or a fixed-size batch with "Load more" or next/previous) with clear pagination controls.
4. **Given** the user has uploaded or processed logs, **When** they view the upload/processing summary (files processed, skipped, lines parsed, rejected, parsed coverage), **Then** this information is presented visually (e.g. charts or graphs) in addition to or instead of plain text, using a suitable charts library.

---

### User Story 2 - Paginated Search Results (Priority: P2)

A user searches the knowledge base and sees results in a paginated list (e.g., a fixed page size with next/previous or "Load more" with a clear page boundary), instead of an unpaginated infinite scroll.

**Why this priority**: Pagination makes result sets manageable, predictable, and easier to navigate; infinite scroll is undesirable for this list.

**Independent Test**: Can be fully tested by running a knowledge-base search and confirming results appear in pages (or discrete "load more" chunks) with visible pagination or page controls.

**Acceptance Scenarios**:

1. **Given** the user is on the knowledge base search, **When** they run a query, **Then** results are shown in pages (or a fixed-size batch with an option to load more), not as a single infinite scroll.
2. **Given** search results are displayed, **When** there are more results than one page, **Then** the user can navigate to the next (and optionally previous) page or load the next batch via a clear control.
---

### User Story 3 - Back to Home Inside Knowledge Space (Priority: P3)

A user in the knowledge space (KB) area can return to the main home/session view using a "Back to Home" (or equivalent) control that is placed within the knowledge space content area, not in the global top navigation bar.

**Why this priority**: Keeps navigation context clear and separates global nav from in-context KB navigation.

**Independent Test**: Can be fully tested by opening the knowledge base view and verifying that the back-to-home control appears within the KB content region and is not in the shared top nav.

**Acceptance Scenarios**:

1. **Given** the user is on the knowledge base view, **When** they look for a way to return to the main home/session view, **Then** the "Back to Home" control is located within the knowledge space content area (e.g., above or beside the KB sections), not in the global top navigation.
2. **Given** the user is on the knowledge base view, **When** they use the back-to-home control, **Then** they are taken to the main session/home view.

---

### User Story 4 - Reduced Repeated Copy and Icons (Priority: P4)

A user sees consistent, non-redundant copy and icons: section headings and body text are not duplicated unnecessarily, and the same icon is not used for unrelated actions (e.g., upload vs. generate report).

**Why this priority**: Reduces visual noise and confusion and improves clarity.

**Independent Test**: Can be fully tested by reviewing the session view and knowledge base view for duplicate headings/descriptions and for icons that are reused for different actions, and confirming they are deduplicated or disambiguated.

**Acceptance Scenarios**:

1. **Given** the user is on any affected screen, **When** they read headings and key copy, **Then** the same phrase is not repeated as both a section title and an identical subheading or body line where it adds no value.
2. **Given** the user is on any affected screen, **When** they look at action buttons or links, **Then** distinct actions (e.g., upload file vs. generate report) use distinct icons or labeling so that the same icon is not reused for semantically different actions without clear differentiation.

---

### User Story 5 - Top Bar Home Link and Application Icon (Priority: P5)

A user can always return to the home/session view by clicking the application name (e.g. "LogPilot") in the top navigation bar. The top bar also displays an application icon (e.g. logs-related) next to or with the application name for quick recognition.

**Why this priority**: Consistent home access from the top bar improves navigation; the icon reinforces brand and context.

**Independent Test**: Can be fully tested by clicking the application name in the top bar from any view and confirming navigation to home, and by verifying an application icon (e.g. logs-related) is visible in the top bar.

**Acceptance Scenarios**:

1. **Given** the user is on any view (including knowledge base), **When** they click the application name in the top navigation bar, **Then** they are taken to the home/session view.
2. **Given** the user is on any view, **When** they look at the top navigation bar, **Then** an application icon (e.g. representing logs or the product) is visible next to or with the application name.

---

### Edge Cases

- What happens when the viewport is small (e.g., laptop or reduced window)? Rearrange only (including use of right-side space); do not add collapsible or compact sections. If content still doesn't fit after rearranging, scrolling is acceptable. Prioritize single-screen fit at typical desktop sizes.
- How does the system handle a very long sessions list? The sessions list MUST be paginated (fixed page size with next/previous or "Load more"); when there are zero or only one page of sessions, pagination controls are hidden or disabled as appropriate.
- What happens when search returns zero results or only one page? Pagination controls should still be present but disabled or hidden as appropriate (e.g., no "Next" when there is only one page).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The main session view MUST arrange content so that the Sessions sidebar and the primary sections (Upload logs, Logs & metrics, Reports) fit on one screen without vertical scrolling at typical desktop viewport sizes.
- **FR-002**: The application MUST use available empty space to achieve the single-screen layout where possible, including taking advantage of the space on the right by moving some sections to the right (e.g. horizontal or multi-column arrangement).
- **FR-003**: Knowledge base search results MUST be presented in a paginated manner (fixed page size with "Load more" and optional "Previous" or back-to-start), not as an unpaginated infinite scroll; the same pagination pattern applies to both KB search and the sessions list.
- **FR-004**: The user MUST be able to load the next batch via a clear "Load more" control and, when applicable, return to the previous batch or start via an optional "Previous" or back-to-start control.
- **FR-005**: The "Back to Home" (or equivalent) control for leaving the knowledge base view MUST be placed within the knowledge space content area, not in the global top navigation bar.
- **FR-006**: The application MUST avoid redundant copy: the same heading or description MUST NOT be repeated unnecessarily (e.g., identical section title and subheading with no added meaning).
- **FR-007**: The application MUST use distinct icons or labeling for distinct actions (e.g., upload vs. generate report) so that the same icon is not reused for semantically different actions without clear differentiation.
- **FR-008**: The application name (e.g. "LogPilot") in the top navigation bar MUST be clickable and MUST navigate the user to the home/session view.
- **FR-009**: The top navigation bar MUST display an application icon (e.g. representing logs or the product) next to or with the application name; implementation may use Lucide React for the icon (e.g. logs-related).
- **FR-010**: The sessions list in the sidebar MUST be presented in a paginated manner (fixed page size with "Load more" and optional "Previous" or back-to-start), not as an unbounded scroll-only list; the same pagination pattern applies to both the sessions list and KB search results.
- **FR-012**: The upload/processing summary (files processed, files skipped, lines parsed, lines rejected, parsed coverage) MUST be presented in a visual form (e.g. charts or graphs) so that the information is easier to scan; implementation may use any suitable charts library.

### Key Entities *(include if feature involves data)*

- **Session list**: The list of sessions in the sidebar; MUST be delivered in fixed-size batches with "Load more" and optional "Previous" or back-to-start (same pattern as KB search results).
- **Search result set**: Knowledge base search results; MUST be delivered in fixed-size batches with "Load more" and optional "Previous" or back-to-start (same pattern as sessions list).
- **Upload/processing summary**: Files processed, files skipped, lines parsed, lines rejected, parsed coverage; must be presented visually (e.g. charts/graphs) using a suitable charts library.
- **Knowledge space view**: The screen containing knowledge base ingestion and search; must contain an in-context "Back to Home" control.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At a typical desktop viewport size, users can see and use the main session view (Sessions, Upload logs, Logs & metrics, Reports) without vertical scrolling.
- **SC-002**: Users can navigate knowledge base search results in discrete pages or batches, with visible pagination or load-more controls.
- **SC-003**: Users can return to the main view from the knowledge base using a control located within the knowledge space content area (not in the global top nav).
- **SC-004**: Affected screens have no unnecessary repeated headings or body copy, and distinct actions use distinct icons or labels so that icon reuse does not cause confusion.
- **SC-005**: From any view, users can reach the home/session view by clicking the application name in the top bar, and the top bar shows an application icon (e.g. logs-related) with the application name.
- **SC-006**: Users can navigate the sessions list in discrete pages or batches, with visible pagination or load-more controls.
- **SC-008**: Upload/processing summary (files processed, skipped, lines parsed, rejected, coverage) is presented visually (e.g. charts or graphs) for easier scanning; any suitable charts library may be used.

## Assumptions

- "Typical desktop viewport" is assumed to be at least 1280×720 or similar; smaller viewports may require scrolling.
- Layout should take advantage of horizontal (right-side) space by moving some sections to the right where appropriate, rather than stacking all content vertically.
- If single-screen cannot be achieved by rearrangement alone (including right-side space), scrolling is acceptable; collapsible or compact sections are out of scope for this feature.
- The sessions list in the sidebar is paginated in this feature (fixed page size with next/previous or "Load more"); the single-screen goal applies to the overall layout including the main content (upload, logs & metrics, reports).
- "Back to Home" is the expected label or equivalent (e.g., "Back to sessions"); the exact wording can follow existing product language.
- Pagination batch size is fixed at 10 items for both the sessions list and KB search results; no user-adjustable batch size control.
- Both the sessions list and KB search use the same pagination pattern: "Load more" for the next batch, with optional "Previous" or back-to-start when applicable.
- A charts library (choice left to implementation/plan) is used to present the upload/processing summary (files processed, skipped, lines parsed, rejected, parsed coverage) visually for better scanability.
