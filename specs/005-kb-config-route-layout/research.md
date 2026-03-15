# Research: Knowledge base config route and layout

**Branch**: `005-kb-config-route-layout`  
**Date**: 2026-03-15  

Resolves design choices for route, header control, and accessibility. No NEEDS CLARIFICATION remained in Technical Context; this document records decisions and alternatives.

---

## 1. Configuration route path

**Decision**: Use `/knowledge` as the configuration route path.

**Rationale**: Spec says "configuration or settings" and "e.g. `/settings` or `/config`". The page is KB-only and labeled "Knowledge base"; a path that matches the label (`/knowledge`) is clearer and more bookmark-friendly than a generic `/settings` when no other settings exist.

**Alternatives considered**:
- `/settings` — Generic; implies future hub; spec chose KB-only for this feature.
- `/config` — Same as above; `/knowledge` is more specific and matches the tooltip label.

---

## 2. Upper-right control placement

**Decision**: Place the KB link (database icon + status indicator) in the main-content navbar, top-right. The navbar is a horizontal bar above the page content (not the left sidebar), visible on every page that uses AppLayout (home and knowledge page). Do not place the control inside the sidebar.

**Rationale**: Spec requires "upper right corner screen option" and "icon with indicator only" with tooltip. The current layout has a left sidebar (sessions) and a main content area with no navbar. Adding a navbar (thin horizontal bar or top bar) in the main area keeps the control visible without changing the sidebar contract and matches common "settings/knowledge" entry points in app UIs.

**Alternatives considered**:
- Sidebar bottom — Would mix session nav with global KB; spec implies a distinct "upper right" entry.
- Floating button — More intrusive; spec implies a normal navigation control.

---

## 3. Status indicator and accessibility

**Decision**: Derive indicator state from existing `GET /knowledge/ingest/status`: red when status is idle and (no last_result or error), yellow when status is running (with pulsating CSS), green when status is idle with last_result and no error. Expose state to assistive technologies via `aria-label` on the control (e.g. "Knowledge base, no data" / "Knowledge base, ingesting" / "Knowledge base, ready") and optional `aria-live` for status changes.

**Rationale**: Backend already exposes `status`, `last_result`, `error`; no API change. Spec requires red for no/empty/failed, yellow for in progress, green for complete. Pulsating is a CSS animation (e.g. `animate-pulse` or custom keyframes). Tooltip shows "Knowledge base" on hover/focus; aria-label adds status for screen readers.

**Alternatives considered**:
- Separate endpoint for "indicator state" — Unnecessary; current status is sufficient.
- No pulsating — Spec explicitly requests pulsating for in-progress.

---

## 4. Return control on Knowledge page

**Decision**: Provide a visible link or button labeled "Back to home" or "Home" at the top of the knowledge page (or in the same navbar as the KB icon), in addition to browser back.

**Rationale**: Spec requires "visible in-app way to return to the main screen". A text link or icon+text at the top is standard and keyboard-accessible; the same navbar can host both "Home" and the KB icon (which on the KB page can remain visible for consistency or show as active).

**Alternatives considered**:
- Browser back only — Spec explicitly requires in-app return.
- Breadcrumb — Heavier; a single "Home" link is sufficient for two-level nav.
