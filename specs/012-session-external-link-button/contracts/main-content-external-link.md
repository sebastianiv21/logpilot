# UI Contract: Main-Content Session External Link Control

**Branch**: `012-session-external-link-button`  
**Date**: 2026-03-15  

Describes the external link control shown in the main content area next to the session title. No API contract changes; sessions API already returns `external_link`.

## Location

- **Where**: Main content area where the session title is displayed (e.g. home page), immediately adjacent to the session title (e.g. to the right of the title).
- **When visible**: Always shown when the session title is shown. When the current session has a non-empty `external_link` (after trimming whitespace), the control is **enabled**; when `external_link` is `null`, `undefined`, or empty/whitespace-only, the control is **disabled** and MUST show a tooltip (e.g. "No external link provided" or "There is no provided link").

## Behavior

- **When enabled**: User can activate by click, keyboard (focus + Enter/Space), or screen reader. Activation opens the session’s `external_link` in a **new tab** (or new window) so the application remains open in the current tab. The `href` of the control MUST be the current session’s `external_link` value. Use `target="_blank"` and `rel="noopener noreferrer"` for security and spec compliance.
- **When disabled**: The control MUST NOT navigate (e.g. use a non-focusable or disabled element, or prevent default and do nothing). A tooltip MUST be shown on hover (and equivalent for keyboard/screen reader, e.g. via `title` or `aria-label`) stating that no link is provided (e.g. "No external link provided").

## Presentation

- **Label**: Visible text MUST be "External link". An icon (e.g. external-link / open-in-new) MUST be shown alongside the text. When disabled, the icon and/or text SHOULD be visually muted (e.g. disabled styling, reduced opacity).
- **Accessibility**: The control MUST be keyboard-focusable (when disabled, focusable for tooltip/announcement). Accessible name: when enabled use e.g. `aria-label="Open session's external link"`; when disabled use e.g. `aria-label="External link — no link provided"` or match the tooltip text. If the icon is decorative, set `aria-hidden="true"` on it.

## Acceptance (from spec)

- Given current session has non-empty `external_link` → control is visible and enabled next to title with icon + "External link"; activating it opens that URL in a new tab.
- Given current session has no external link → control is visible but disabled, with a tooltip (e.g. "No external link provided"); activating it does nothing.
- Keyboard and screen reader users can focus the control and, when enabled, activate it for the same navigation as pointer users; when disabled, they hear/see that no link is provided.
