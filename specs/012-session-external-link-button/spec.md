# Feature Specification: Session External Link Button in Main Content

**Feature Branch**: `012-session-external-link-button`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "Add a button in the main content, it could be placed at the right of the title, to go to an external link provided in the session creation if it's available. Use the required skills for the job."

## Clarifications

### Session 2026-03-15

- Q: When the user activates the external-link control, should the link open in the same browser tab or in a new tab/window? → A: New tab (or new window) — open the link in a new tab so the app stays open in the current tab.
- Q: Should the external-link control show visible text or be icon-only with tooltip/aria-label? → A: Both — icon and visible text (e.g. icon + "Open session's external link") next to the title, so users understand it is the external link they provided in the session (create/edit) form. Refined: use the shorter label "External link" with an appropriate icon (e.g. external-link / open-in-new); placement next to the session title makes the association clear.
- When there is no provided external link: show the control (icon + text) in a disabled state with a tooltip saying there is no provided link (e.g. "No external link provided") instead of hiding it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open Session External Link from Main Content (Priority: P1)

When viewing a session in the main content area, the user sees a control next to the session title that, when activated, takes them to the external link associated with that session—when such a link was provided at session creation or later. This lets users quickly reach related resources (e.g. tickets, runbooks, dashboards) without leaving the flow.

**Why this priority**: The primary value is one-click access to the session’s external reference from the main screen; without it, users must remember or look up the link elsewhere.

**Independent Test**: Can be fully tested by creating or selecting a session that has an external link set, confirming a control appears next to the title and is enabled, activating it, and verifying the user is taken to that link. For sessions without an external link, the control is visible but disabled with a tooltip indicating no link is provided.

**Acceptance Scenarios**:

1. **Given** the user is viewing a session that has an external link set (at creation or via edit), **When** the main content area shows the session title, **Then** a control (e.g. button or link) is visible next to the title showing both an appropriate icon (e.g. external-link) and visible text "External link" so users understand it opens the session’s external link (the one provided in the session form), and allows the user to go to that link.
2. **Given** the user is viewing a session that has no external link set, **When** the main content area shows the session title, **Then** the external-link control is visible next to the title but in a disabled state, with a tooltip (e.g. "No external link provided" or "There is no provided link") so the user understands why it cannot be activated.
3. **Given** the external-link control is visible and enabled (session has an external link), **When** the user activates it, **Then** the external link opens in a new tab (or new window) so the app remains open in the current tab, and the link is the one stored for that session.
4. **Given** the external-link control is visible and enabled, **When** the user focuses and activates it via keyboard or screen reader, **Then** the same navigation to the external link occurs as with pointer activation.

---

### Edge Cases

- **Session has an empty or whitespace-only external link**: Treated as no link; the control is shown in a disabled state with a tooltip (e.g. "No external link provided").
- **External link is invalid or unreachable**: When a link is set, activation still attempts navigation; the browser or system handles failure (e.g. error page, broken link). The feature does not block activation; validation of the URL is out of scope for this feature.
- **User switches to a different session**: The control stays visible and updates to enabled or disabled (with tooltip) according to whether the newly selected session has a non-empty external link.
- **Session data is updated (e.g. external link added or removed)**: After the main content reflects the updated session, the control is enabled when the current session has a non-empty external link and disabled with tooltip when it does not.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: In the main content area where the session title is displayed, the system MUST always show the external-link control (icon and visible text "External link") next to the title. When the session has a non-empty external link set (from creation or update), the control is enabled and navigates to that link when activated; when the session has no external link (missing, null, or empty/whitespace-only), the control MUST be disabled and MUST show a tooltip (e.g. "No external link provided" or "There is no provided link").
- **FR-002**: The control MUST be placed next to the session title (e.g. to the right of the title) so it is clearly associated with the current session.
- **FR-003**: When the current session has no external link (missing, null, or empty/whitespace-only), the system MUST follow FR-001: show the external-link control in a disabled state with a tooltip (e.g. "No external link provided").
- **FR-004**: When the control is enabled, activating it MUST open the session’s external link in a new tab (or new window) so the application stays open in the current tab; the link opened MUST be the one stored for the current session. When the control is disabled, it MUST NOT navigate.
- **FR-005**: The external-link control MUST show both an appropriate icon (e.g. external-link / open-in-new) and the visible text "External link"; placement next to the session title conveys that it is the session’s external link (from the session form). The control MUST be keyboard-focusable and MUST have an accessible name (e.g. aria-label such as "Open session's external link" when enabled, or "External link — no link provided" when disabled) so screen reader and keyboard users understand its state; when disabled, the tooltip and/or aria-label MUST explain that there is no provided link.

### Assumptions

- Sessions already support an optional external link field at creation and update; the feature exposes it in the main content next to the title. When no link is set, the control is always shown but disabled with a tooltip.
- The main content area and session title are already defined elsewhere; this feature adds a single control that is always visible next to the title and is enabled or disabled (with tooltip) depending on the presence of the session’s external link.

### Key Entities

- **Session**: Has an optional external link (URL) provided at creation or via update. The control is always shown; it is enabled when this value is present and non-empty, and disabled with a tooltip when it is not.
- **Main content title**: The place where the current session’s title is shown; the control is placed next to it (e.g. to the right).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users with a session that has an external link can reach that link in one action from the main content (e.g. one click or one keyboard activation) without searching elsewhere.
- **SC-002**: When a session has no external link, the control is visible but disabled and shows a tooltip (e.g. "No external link provided") so users understand the feature exists but no link is set.
- **SC-003**: Keyboard and screen reader users can focus the external-link control and, when it is enabled, activate it to achieve the same navigation as pointer users.
- **SC-004**: The control is unambiguously tied to the current session so users do not open a link for a different session by mistake.
