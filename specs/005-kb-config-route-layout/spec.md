# Feature Specification: Knowledge base config route and layout improvements

**Feature Branch**: `005-kb-config-route-layout`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "The knowledge base ingestion menu is shared across the sections. I would prefer that the section is in another route, like if it were a configuration or something like that. You can include that as part of an upper right corner screen option. Let's also evaluate how the layout is shown and if we can do something to rearrange it in a better way to have a better user experience."

## Clarifications

### Session 2026-03-15

- Q: Upper-right control behavior — does it navigate to the config route on click or open a dropdown/menu? → A: Navigate on click; control is a direct link to the configuration page (single click goes to config route).
- Q: Configuration route scope — KB-only page or config hub for future settings? → A: KB-only page; the route shows only the knowledge base (ingestion and search). No placeholder or structure for other settings in this feature.
- Q: Session scope when opening the configuration page — is the knowledge base session-scoped or global? → A: Global; the knowledge base is independent of sessions and always usable from the configuration page without requiring a session to be selected.
- Q: Main screen section order — keep current order or reorder? → A: Keep current order (intro, upload logs, logs & metrics, reports); only improve visual hierarchy (headings, spacing, grouping).
- Q: Returning from the configuration page — browser back only or explicit in-app return? → A: Explicit in-app return; the configuration page MUST include a visible way to return to the main screen (e.g. "Back to home" or "Home" link/button), in addition to browser back.
- **User preference**: Upper-right control uses the database icon (same as used for the knowledge base elsewhere). The control MUST show a small status indicator (e.g. colored dot) reflecting knowledge base state: red = no/empty KB, yellow/ochre = ingestion in progress (with a pulsating effect), green = KB available/complete.
- **User preference**: The control is labeled "Knowledge base". The visible option is only the icon with the status indicator (no text label). A tooltip MUST show the label "Knowledge base" when the user hovers or focuses the control.
- Q: Status indicator when the last ingestion run failed — red (same as no KB) or distinct error state? → A: Red (same as no KB); no separate "error" state for the indicator. The config page may still show the error message.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open knowledge base from upper-right control (Priority: P1)

A user can open a configuration or settings area from a control in the upper-right area of the screen (e.g. an icon or menu). From there they can reach the knowledge base ingestion and search without those controls appearing on the main home/session screen.

**Why this priority**: This is the primary behavioral change—moving KB out of the main flow and making it reachable from a dedicated entry point.

**Independent Test**: Can be fully tested by using the upper-right control to open configuration, then performing ingestion or search; delivers clear separation of “session work” vs “configuration.”

**Acceptance Scenarios**:

1. **Given** the user is on any main app screen, **When** they activate the upper-right control (database icon), **Then** they can navigate to a dedicated configuration/settings view.
2. **Given** the user has opened the configuration view, **When** they look at the page, **Then** they see the knowledge base ingestion and search options available there.
3. **Given** the user is on the main home/session screen, **When** they view the page, **Then** the knowledge base ingestion block is not shown on that screen.
4. **Given** the user is on any main app screen, **When** they look at the upper-right control, **Then** they see only the database icon with the status indicator (no visible text). **When** they hover or focus the control, **Then** a tooltip shows the label "Knowledge base". The indicator is red when there is no knowledge base, yellow/ochre (pulsating) when ingestion is in progress, and green when the knowledge base is available and complete.

---

### User Story 2 - Knowledge base on its own route (Priority: P2)

The knowledge base (ingestion and search) lives on a dedicated route (e.g. configuration or settings). Users can open it via the upper-right control and can also reach it directly via URL or browser back/forward.

**Why this priority**: Ensures KB is treated as a distinct “place” in the app, improving clarity and bookmarkability.

**Independent Test**: Can be tested by navigating to the config route directly, then running ingestion or search; delivers a single, clear place for KB operations.

**Acceptance Scenarios**:

1. **Given** the app is loaded, **When** the user navigates to the configuration route (e.g. via URL or in-app link), **Then** they see the knowledge base section (ingestion and search) on that page.
2. **Given** the user is on the configuration route, **When** they use the in-app return control (e.g. "Back to home" or "Home") or browser back, **Then** they return to the main screen without losing app state where applicable.
3. **Given** the user bookmarks or shares the configuration URL, **When** they open it later, **Then** they land on the configuration page with knowledge base options visible.

---

### User Story 3 - Improved layout and information hierarchy (Priority: P3)

The main screen and the configuration screen have a clear, improved layout so that sections are easier to scan, the hierarchy of actions is obvious, and the overall experience feels less cluttered and more focused.

**Why this priority**: Improves usability after the structural change; depends on P1/P2 being in place.

**Independent Test**: Can be tested by walking through main screen and config screen and verifying that headings, spacing, and grouping make the purpose of each area obvious and reduce cognitive load.

**Acceptance Scenarios**:

1. **Given** the user is on the main screen, **When** they view the page, **Then** the sections appear in the current order (intro, upload logs, logs & metrics, reports) with clear visual hierarchy (headings, spacing, grouping).
2. **Given** the user is on the configuration screen, **When** they view the page, **Then** knowledge base ingestion and search are grouped and labeled so it is clear they belong together.
3. **Given** the user navigates between main and configuration, **When** they move between screens, **Then** the transition feels consistent and the role of each screen is clear.

---

### Edge Cases

- What happens when the user opens the configuration route directly (e.g. from a bookmark) before visiting the home page? They see the configuration page with knowledge base options; the KB is global so ingestion and search are always available without a session.
- How does the system handle keyboard and assistive users? The upper-right control (icon + indicator only, tooltip "Knowledge base") and configuration route must be reachable via keyboard and announced as "Knowledge base" so the purpose is clear.
- What happens when the user has no session selected and opens configuration? The knowledge base is global and independent of sessions; the configuration page is fully usable (ingestion and search) and does not require a session to be selected.
- What happens when the last ingestion run failed? The status indicator shows red (same as no/empty KB). The configuration page may still display the error message; no separate indicator state for "failed."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST provide an upper-right control in the main-content navbar that shows only the database icon and the status indicator (no visible text label). The control MUST have a tooltip that displays the label "Knowledge base" on hover or focus. On activation (single click), it MUST navigate directly to the configuration/settings route (no dropdown or intermediate menu).
- **FR-001b**: The upper-right control MUST display a visible status indicator (e.g. a small colored dot) reflecting the knowledge base state: red when there is no knowledge base, it is empty, or the last ingestion run failed; yellow/ochre when ingestion is in progress, with a pulsating effect to signal progress; green when the knowledge base is available and complete.
- **FR-002**: The knowledge base ingestion and search MUST be available only on a dedicated configuration/settings route, not on the main home or session screen.
- **FR-003**: Users MUST be able to reach the configuration view by activating the upper-right control and by navigating directly to the configuration route (e.g. via URL).
- **FR-004**: The main screen MUST present a clear layout for the remaining sections in the current order (session intro, then upload logs, then logs & metrics, then reports), with improved visual hierarchy (headings, spacing, grouping); section order MUST NOT be changed.
- **FR-005**: The configuration screen MUST present the knowledge base (ingestion and search) as a coherent group with clear labeling and hierarchy.
- **FR-006**: Navigation between the main screen and the configuration screen MUST be consistent and clearly indicate which screen the user is on (e.g. active state or title). The configuration page MUST provide a visible in-app way to return to the main screen (e.g. "Back to home" or "Home" link/button), in addition to browser back.
- **FR-007**: The upper-right control and configuration route MUST be usable with keyboard and compatible with common assistive technologies (focus order, labels, and structure). The control MUST be announced as "Knowledge base" (e.g. via tooltip and aria-label or title). The status indicator state (no KB / in progress / complete) MUST be communicated to assistive technologies (e.g. via aria-label or live region).

### Key Entities

- **Configuration view**: The dedicated screen or route that shows only the knowledge base (ingestion and search). Reachable from the upper-right control and by direct navigation. No other settings or sections in scope for this feature. The knowledge base is global (independent of sessions), so the configuration page is always usable without a session selected.
- **Main screen**: The primary app view (e.g. home/session) that shows session-related actions (upload logs, logs & metrics, reports) and no longer shows the knowledge base section.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open the knowledge base (ingestion and search) from the upper-right control within two actions (e.g. click control, then see KB or click config then KB).
- **SC-002**: Users can reach the configuration page via direct URL and see the knowledge base section without errors.
- **SC-003**: The main screen no longer displays the knowledge base block; all KB actions are completed from the configuration route.
- **SC-004**: Layout and hierarchy on main and configuration screens pass a simple heuristic: a first-time user can identify “where to do session work” vs “where to manage knowledge base” within a short scan of each screen.
- **SC-005**: Keyboard-only users can focus the upper-right control, activate it, and reach the knowledge base section on the configuration page.
- **SC-006**: Users can tell at a glance from the upper-right control whether the knowledge base is missing (red), in progress (yellow/ochre, pulsating), or ready (green).

## Assumptions

- The upper-right control lives in the main-content navbar (top bar above the page content). It shows only the database icon with the status indicator; the label "Knowledge base" is shown via tooltip (on hover/focus) and announced for assistive technologies. Status indicator: red = no/empty KB, yellow/ochre = in progress (pulsating), green = KB available/complete.
- The configuration route has a stable path `/knowledge` for direct links and bookmarks (per research.md).
- “Layout improvement” means clearer grouping, headings, and spacing rather than a full visual redesign; no change to the underlying data or backend behavior. Main screen section order stays as-is (intro, upload logs, logs & metrics, reports); only visual hierarchy is improved.
- The knowledge base is global and independent of sessions; the configuration page is always usable and does not require a session to be selected for ingestion or search.
- **Out of scope**: Other settings (e.g. API URL, theme, general app preferences) are not part of this feature; the configuration route is KB-only.
