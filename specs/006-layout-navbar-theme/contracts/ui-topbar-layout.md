# UI Contract: Top bar and layout (theme, sidebar, branding)

**Branch**: `006-layout-navbar-theme`  
**Date**: 2026-03-15  

Defines the UI contract for the top bar (navbar), theme switcher, conditional sidebar, and LogPilot branding. Implementation must satisfy these so that acceptance tests and manual validation can rely on them.

---

## 1. Top bar (navbar)

- **Visibility**: Present on every page that uses AppLayout (home `/` and knowledge `/knowledge`). Horizontal bar above the main content; distinct from the left sidebar.
- **Order (left to right)**:
  1. **LogPilot**: Application name (e.g. text or logo). Must be present and must not appear in the left sidebar on any page.
  2. **Nav (conditional)**: When on `/knowledge`, a visible "Back to home" (or equivalent) link. When on `/`, no back link or equivalent spacing.
  3. **HeaderKbLink**: Existing database icon + status indicator (unchanged).
  4. **Theme switcher**: Last item in the navbar. Single control that toggles between at least two themes (e.g. light/dark); sun/moon swap or equivalent. Must be keyboard-accessible and persist choice across reloads (e.g. via theme-change and localStorage).
- **Accessibility**: Skip-to-main-content link and focus order remain valid. Theme switcher and LogPilot placement are focusable and announced appropriately.

---

## 2. Left sidebar (sessions)

- **When visible**: On home (`/`) only. Contains "Sessions" heading, current session summary, create-session control, and session list. Does not contain "LogPilot".
- **When hidden**: On knowledge page (`/knowledge`). The entire left sidebar (sessions list and create-session controls) must not be visible. Main content and top bar remain usable; no critical action depends solely on the hidden sidebar.

---

## 3. Theme switcher

- **Placement**: Last item in the top bar only.
- **Behavior**: Single action toggles theme (e.g. light ↔ dark). Chosen theme applies immediately and persists after full page reload. Default when no stored preference: system preference (OS/browser light or dark); if unavailable, "light".
- **Implementation**: theme-change library (e.g. `data-toggle-theme="dark,light"` or equivalent); init with `themeChange(false)` in React (e.g. in root or main.tsx).

---

## 4. Home page content

- **Copy**: The exact phrase "Upload logs or switch session in the sidebar." must not appear anywhere on the home page.
- **When no session selected**: One short instructional line must be displayed (e.g. "Select or create a session to get started.").
- **Heading**: The main content area must not use "LogPilot" as the primary page title/heading (branding lives in the top bar).

---

## 5. Knowledge page

- **Layout**: No left sidebar. Top bar visible with LogPilot, "Back to home", HeaderKbLink, and theme switcher. Main content: knowledge base ingestion and search only.
- **Return**: "Back to home" (or equivalent) in the top bar navigates to `/`.
