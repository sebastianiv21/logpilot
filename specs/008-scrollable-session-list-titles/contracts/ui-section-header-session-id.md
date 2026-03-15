# UI Contract: Section Header with Session Title and Copy ID

**Branch**: 008-scrollable-session-list-titles  
**Date**: 2026-03-15  

Describes the UI behavior and inputs for the Logs & metrics and Reports section headers: dynamic session title, session ID line, and copy control. No backend API; frontend component contract.

---

## 1. Section title (dynamic)

**Behavior**:
- When there is a **current session** with a **name**: display the session name as the section heading.
- When there is a **current session** with **no name**: display `"Session " + id.slice(0, 8)` (same prefix as session list).
- When there is **no current session**: display placeholder text (e.g. "No session selected").
- When the session name is **too long**: truncate with ellipsis; expose full name on hover via `title` or tooltip.

**Inputs (advisory)**:
- `currentSession: Session | null` — from sessions list lookup by `currentSessionId`.
- Or: `titleText: string` (already computed: name, "Session xxxxxxxx", or placeholder).
- For long name: `titleAttribute?: string` (full name for `title` / tooltip).

**Accessibility**: Heading level and id preserved for section (e.g. `id="logs-metrics-heading"` / `id="reports-heading"`); truncated title still has full name on hover for screen readers that expose title.

---

## 2. Session ID line (below title)

**Behavior**:
- Shown **only when** there is a current session.
- Displays the **full session ID** (e.g. UUID or full string from API).
- Includes a **copy** control (button with icon) that copies the full ID to the clipboard.
- Copy control has **accessible name** (e.g. `aria-label="Copy session ID"`).
- On **success**: show toast (e.g. Sonner success "Session ID copied").
- On **failure**: show toast (e.g. Sonner error "Copy failed" or "Couldn't copy").

**Inputs (advisory)**:
- `sessionId: string` — full session ID (only when current session exists).
- `onCopySuccess?: () => void` / `onCopyError?: (err: unknown) => void` — or use toast directly in component.

**Accessibility**: Copy button is a `<button>`, focusable, with `aria-label="Copy session ID"`. Icon can have `aria-hidden="true"`.

---

## 3. Where used

- **Logs & metrics** section: one section header (title + optional session ID line + copy).
- **Reports** section: one section header (title + optional session ID line + copy).
- Same pattern for both; can be a shared component (e.g. `SessionSectionHeader`) or inline markup that follows this contract.
