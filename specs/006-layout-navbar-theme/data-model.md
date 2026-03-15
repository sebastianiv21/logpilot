# Data Model: App layout and navigation improvements

**Branch**: `006-layout-navbar-theme`  
**Date**: 2026-03-15  
**Source**: Feature spec. No new backend entities or API schema; this document describes client-only state (theme preference, route-driven layout).

---

## 1. No new domain entities

This feature does not add new backend entities, tables, or API contracts. It adds:

- **Theme preference**: Stored in the browser via the theme-change library (localStorage key `theme` by default). Values: `"light"` | `"dark"` (or other theme names if extended). No server-side user preferences.
- **Route-driven layout**: Current path (`/` vs `/knowledge`) determines whether the left sidebar is visible; derived from React Router `location.pathname`, no new global store.

---

## 2. Theme preference (client-only)

**Source**: theme-change library; persistence in localStorage.

- **Key**: `theme` (default; configurable via `data-key` if needed).
- **Values**: At least `"light"` and `"dark"`. Default when key missing: apply system preference (`prefers-color-scheme: dark` → `"dark"`, else `"light"`); if system preference unavailable, use `"light"`.
- **Document**: `document.documentElement.getAttribute('data-theme')` reflects current theme; theme-change sets it on toggle and on init.
- **No server**: No API or backend storage for theme.

---

## 3. Layout state (client-only)

- **Sidebar visible**: `true` when `location.pathname !== '/knowledge'`; `false` when `location.pathname === '/knowledge'`.
- **Top bar**: Always visible when AppLayout is used (home and knowledge page). Content: LogPilot, optional "Back to home" (on knowledge page), HeaderKbLink, theme switcher (last). No new persistent state; layout is a function of route.

---

## 4. Home page copy and branding

- **Removed**: The exact phrase "Upload logs or switch session in the sidebar." must not appear.
- **When no session selected**: One short instructional line (e.g. "Select or create a session to get started.") must be displayed.
- **LogPilot**: Rendered only in the top bar (not in the left sidebar). Home page main content must not use "LogPilot" as the primary page heading.

No new fields or tables; validation is copy and DOM structure.
