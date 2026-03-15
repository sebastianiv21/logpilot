# Research: App layout and navigation improvements

**Branch**: `006-layout-navbar-theme`  
**Date**: 2026-03-15  

Resolves design choices for theme switching (theme-change library), default theme (system preference), and top bar layout. Spec and clarifications already fixed theme-change as the implementation library; this document records integration details and alternatives.

---

## 1. Theme switching: theme-change library

**Decision**: Use the [theme-change](https://github.com/saadeghi/theme-change) library for the theme switcher control and persistence. The app already depends on `theme-change` (frontend package.json).

**Rationale**: Spec and user explicitly require theme-change. It uses `data-theme` on the document root and localStorage for persistence; supports `data-toggle-theme="dark,light"` for a single toggle control; works with React when initialized once with `themeChange(false)` (e.g. in `useEffect` in a root component or `main.tsx`). No NEEDS CLARIFICATION; implementation follows library docs.

**Alternatives considered**:
- DaisyUI theme-controller only (CSS + manual localStorage): Spec chose theme-change for persistence and toggle behavior; daisyUI theme-controller can be used as the *markup* (e.g. swap with `theme-controller` class) while theme-change drives the actual theme and storage, or theme-change attributes can be used directly (e.g. `data-toggle-theme`).
- Custom implementation: Unnecessary; theme-change is small and matches requirements.

**Integration**: Call `themeChange(false)` once after app mount (e.g. in `main.tsx` or AppLayout). Use a control with `data-toggle-theme="dark,light"` (or "light,dark" per desired default toggle order). Store key is `theme` by default. For system preference as default when no stored theme: on first load, if no `theme` in localStorage, set `data-theme` from `prefers-color-scheme` (e.g. "dark" or "light") before first paint if possible, or set it in the same init path so theme-change does not overwrite it; theme-change allows setting initial theme via the attribute.

---

## 2. Default theme (system preference, fallback light)

**Decision**: When the user has never set a theme (or clears storage), use system preference (`prefers-color-scheme: dark` → "dark", else "light"). If the media query is unavailable or not supported, default to "light". Apply before or at first paint to avoid flash; document in quickstart and implementation.

**Rationale**: Spec clarification: "Default to system preference (light/dark from OS/browser); fall back to light if unavailable." theme-change does not set system preference by default; the app must set `data-theme` (or the initial theme) on load when localStorage is empty, using `window.matchMedia('(prefers-color-scheme: dark)').matches` and then optionally listen for `prefers-color-scheme` changes if we want to respect OS changes when the user has not explicitly chosen a theme (optional; spec does not require live sync).

**Alternatives considered**:
- Always default to "light": Spec requires system preference when available.
- Persist "system" as a third option: Spec says at least two themes (light/dark) and default "when unavailable" to light; keeping two themes and a one-time default from system is sufficient for MVP.

---

## 3. Top bar structure and daisyUI swap

**Decision**: Top bar (navbar) contains, in order: (1) "LogPilot" (left), (2) optional nav (e.g. "Back to home" when on `/knowledge`), (3) HeaderKbLink (existing), (4) theme switcher as the last item. Use a sun/moon swap or toggle for the theme control; markup can use daisyUI swap + theme-change `data-toggle-theme` (and optionally `data-act-class` for active state), or theme-change’s native toggle behavior. Ensure the control is the last element in the navbar for consistent placement.

**Rationale**: Spec: theme switcher "last item in the navbar"; LogPilot "in the top bar" only; existing top bar has "Back to home" and HeaderKbLink. Order is left-to-right: branding, then back link (when applicable), then KB link, then theme switcher.

**Alternatives considered**:
- Theme switcher in sidebar: Spec says top bar only.
- LogPilot in sidebar: Spec says top bar only; sidebar must not show LogPilot.

---

## 4. Sidebar visibility by route

**Decision**: When `location.pathname === '/knowledge'`, do not render the left sidebar (sessions list and create-session controls). When on `/`, render the sidebar. Use React Router’s `useLocation()` in AppLayout; conditional rendering or conditional class (e.g. hide with CSS) is sufficient. Main content and skip link remain available when sidebar is hidden.

**Rationale**: Spec FR-003 and User Story 2: "When the user is on the knowledge base page, the left sidebar ... MUST NOT be visible." No new route or API; layout only.

---

## 5. FART (Flash of wrong theme) prevention

**Decision**: Set the initial `data-theme` (or equivalent) as early as possible—e.g. an inline script in `index.html` that runs before React, reading localStorage and, if empty, `prefers-color-scheme`, and setting `document.documentElement.setAttribute('data-theme', ...)`. theme-change uses `data-theme`; so setting it before first paint avoids a visible flash. Alternatively, call theme-change init (and set default from system if no stored theme) in the same synchronous block as the first script in the app entry; document the approach in quickstart.

**Rationale**: Common practice for theme UIs; theme-change README mentions FART for Astro and suggests inline script for critical theme set. For React, either inline in HTML or the earliest possible effect in the app root is acceptable.

**Alternatives considered**:
- No early script: Risk of flash of default theme then switch; worse UX.
- Server-side theme: Out of scope; no server-side user prefs in this feature.
