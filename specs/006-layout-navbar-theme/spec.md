# Feature Specification: App layout and navigation improvements

**Feature Branch**: `006-layout-navbar-theme`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "Improve app layout: theme switcher (daisyUI swap), hide sessions sidebar on knowledge page, remove sidebar copy, move LogPilot into top bar"

## Clarifications

### Session 2026-03-15

- Q: Default theme on first visit (light / dark / system)? → A: Default to system preference (light/dark from OS/browser); fall back to light if unavailable.
- Q: Replacement copy on home when no session is selected? → A: Require one short instructional line (e.g. "Select or create a session to get started.").
- Q: Theme switcher location (sidebar / top bar / both)? → A: Top bar only, as the last item in the navbar.
- Q: Where does LogPilot appear (left sidebar vs top bar)? → A: Top bar only; LogPilot does not appear in the left sidebar.
- Implementation choice (theme switching): Use the theme-change library (https://github.com/saadeghi/theme-change) for the theme switcher control and persistence.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Theme switcher (Priority: P1)

A user can change the application theme (e.g. light/dark) using a single control in the top bar (last item in the navbar) that toggles between two states (e.g. sun/moon swap). The chosen theme applies immediately and, when supported, persists across page reloads so returning users see their last choice.

**Why this priority**: Theme choice affects readability and comfort for every user; a visible control is a top layout/UX ask.

**Independent Test**: Can be fully tested by opening the app, using the theme control to switch theme, verifying the UI updates, then reloading and confirming the same theme is still applied.

**Acceptance Scenarios**:

1. **Given** the user is on any page, **When** they use the theme switcher control, **Then** the application theme changes immediately (e.g. light to dark or vice versa).
2. **Given** the user has selected a theme, **When** they refresh the page or navigate away and back, **Then** the same theme is still applied (persistence).
3. **Given** the user has never set a theme, **When** they first load the app, **Then** the theme follows system preference (e.g. OS/browser light or dark); if system preference is unavailable, default to light.

---

### User Story 2 - Hide sessions sidebar on knowledge page (Priority: P2)

When the user is on the knowledge base page, the left sidebar that shows the sessions list (and session creation) is not visible. Only the main content area and its top navigation (e.g. “Back to home”, knowledge-base link) are shown, so the knowledge page is not cluttered with session management.

**Why this priority**: Clear separation between “sessions & logs” and “knowledge base” reduces confusion and matches user expectation that knowledge is a distinct area.

**Independent Test**: Can be fully tested by navigating to the knowledge page and confirming the left sidebar is hidden, then navigating home and confirming the sidebar is visible again.

**Acceptance Scenarios**:

1. **Given** the user navigates to the knowledge base page, **When** the page loads, **Then** the left sidebar (sessions list and create-session controls) is not visible.
2. **Given** the user is on the knowledge page, **When** they use the top navigation to go back to home, **Then** the left sidebar is visible again with the sessions list.
3. **Given** the user is on the knowledge page, **When** the layout is rendered, **Then** the main content and top bar remain usable and accessible (e.g. skip link, focus order).

---

### User Story 3 - Remove sidebar instruction copy (Priority: P3)

The home page no longer displays the text “Upload logs or switch session in the sidebar.” Any equivalent instruction is either removed or rephrased so that it does not refer to “the sidebar” in that way, and does not appear when it would be redundant or confusing.

**Why this priority**: Copy cleanup improves clarity and avoids referencing UI that may be hidden on other pages.

**Independent Test**: Can be fully tested by opening the home page and confirming the exact phrase “Upload logs or switch session in the sidebar.” is not present.

**Acceptance Scenarios**:

1. **Given** the user is on the home page, **When** they view the content, **Then** the text “Upload logs or switch session in the sidebar.” is not displayed.
2. **Given** the user has no session selected, **When** they are on the home page, **Then** they see one short instructional line (e.g. "Select or create a session to get started.").

---

### User Story 4 - LogPilot branding in top bar (Priority: P4)

The application name “LogPilot” is shown in the top bar (navbar) on every page. It does not appear in the left sidebar. Users consistently see the product name in the top bar, and the main content area (e.g. home page) does not duplicate it as the primary page heading.

**Why this priority**: Branding in the top bar keeps it visible on all pages (including when the sidebar is hidden) and avoids duplication in the main content.

**Independent Test**: Can be fully tested by opening the app on home and on the knowledge page, confirming “LogPilot” appears in the top bar and not in the left sidebar, and ensuring the home page main content does not use "LogPilot" as the primary page title.

**Acceptance Scenarios**:

1. **Given** the user is on any page, **When** they view the top bar, **Then** “LogPilot” is displayed there (e.g. as title or logo text).
2. **Given** the user is on the home page, **When** they view the left sidebar, **Then** "LogPilot" is not displayed in the sidebar (only sessions list and related controls appear there).
3. **Given** the user is on the home page, **When** the layout is updated, **Then** the main content heading no longer duplicates “LogPilot” as the primary page title (branding lives in the top bar).

---

### Edge Cases

- **Theme persistence**: If the user has never set a theme or clears storage, the app uses the default: system preference (OS/browser light or dark) when available, otherwise light. No error is shown.
- **Knowledge page without sidebar**: All actions available from the knowledge page (e.g. back to home, knowledge-base link) remain available via the visible top bar; no critical action depends solely on the hidden sidebar.
- **Accessibility**: Theme switcher and “LogPilot” placement remain keyboard-accessible and work with screen readers; skip-to-main-content and focus order remain valid when the sidebar is hidden.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST provide a single theme switcher control that toggles between at least two themes (e.g. light and dark). The control MUST be in the top bar (navbar), as the last item.
- **FR-002**: The application MUST persist the user’s theme choice across page reloads (e.g. via browser storage).
- **FR-003**: When the user is on the knowledge base page, the left sidebar that contains the sessions list and session-creation controls MUST NOT be visible.
- **FR-004**: The home page MUST NOT display the exact phrase “Upload logs or switch session in the sidebar.”
- **FR-004b**: When no session is selected, the home page MUST display one short instructional line directing the user to select or create a session (e.g. "Select or create a session to get started.").
- **FR-005**: The application name "LogPilot" MUST be displayed in the top bar (navbar) on every page; it MUST NOT appear in the left sidebar.

### Key Entities

- **Theme preference**: User’s chosen theme (e.g. light/dark); stored in the browser for persistence; no server entity required.
- **Route/context**: Current page (home vs. knowledge) determines whether the left sidebar is shown; no new data model, only layout rules.

## Assumptions

- Theme options are at least “light” and “dark”; additional themes may be added later.
- Persistence is achieved via browser storage (e.g. local storage); no server-side user preferences in scope.
- Theme switching is implemented using the theme-change library ([theme-change](https://github.com/saadeghi/theme-change)); the implementation plan and tasks must use this library for the theme switcher control and for persisting the chosen theme (e.g. toggle between light/dark, localStorage).
- “Left navbar” and “left sidebar” refer to the same vertical area that currently shows “Sessions” and the session list on the home flow.
- The knowledge page continues to have a top bar with “Back to home” and the knowledge-base link; no change to that top bar’s purpose.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can change theme with one action and see the result immediately; the chosen theme persists after a full page reload in at least one supported browser.
- **SC-002**: On the knowledge base page, the sessions sidebar is not visible; layout can be verified by visual inspection or automated checks.
- **SC-003**: The phrase “Upload logs or switch session in the sidebar.” does not appear anywhere on the home page (text search or accessibility tree).
- **SC-004**: "LogPilot" appears in the top bar on every page and does not appear in the left sidebar; the product name is always present in the top bar.
