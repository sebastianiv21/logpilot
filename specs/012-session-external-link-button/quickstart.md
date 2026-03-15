# Quickstart: Session External Link Button in Main Content

**Branch**: 012-session-external-link-button  
**Date**: 2026-03-15  

Minimal steps to run and validate the main-content external link control. Assumes backend and frontend are running per project docs.

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`) with sessions API (existing).
- **Frontend** dev server running (e.g. `cd frontend && pnpm dev`).

---

## 1. Control visible when session has external link (FR-001, FR-002)

1. Create a **new session** and set the **External link** field (e.g. `https://example.com`) in the create form, or edit an existing session and set **External link**. Save.
2. **Select that session** so it is the current session (main content shows its title).
3. Confirm an **"External link"** control (icon + text) appears **next to the session title** (e.g. to the right).
4. Confirm the control is clearly associated with the current session (same row or block as the title).

---

## 2. Control disabled with tooltip when no external link (FR-003)

1. Select a session that has **no external link** set (or create one without filling External link).
2. Confirm the **"External link"** control (icon + text) is **visible** next to the title but **disabled** (e.g. muted styling, not clickable).
3. Hover (or focus) the disabled control and confirm a **tooltip** appears (e.g. "No external link provided" or "There is no provided link"). Activating it does nothing.
4. Edit a session that had an external link and **clear** the External link field; save. Confirm the control becomes **disabled** with the same tooltip when that session is current.

---

## 3. Opens in new tab when enabled (FR-004)

1. With a session that has an external link set, ensure the **"External link"** control is visible and **enabled** (clickable).
2. **Click** the control. Confirm the link opens in a **new tab** and the app remains open in the **current tab**.
3. Confirm the opened URL is the one you set in the session form.

---

## 4. Keyboard and screen reader (FR-005, SC-003)

1. With the control **enabled** (session has external link), use **keyboard only**: Tab to focus the "External link" control, then Enter or Space to activate. Confirm the same new-tab navigation occurs as with a click.
2. With a **screen reader** enabled, focus the control when enabled and confirm it has an **accessible name** (e.g. "Open session's external link"). When **disabled**, focus the control and confirm the accessible name or tooltip indicates no link is provided (e.g. "External link — no link provided").

---

## 5. Session switch and update (edge cases)

1. Select **session A** (with external link) → control visible and **enabled**. Switch to **session B** (no external link) → control stays visible but becomes **disabled** with tooltip. Switch back to A → control becomes **enabled** again.
2. With session A selected, **edit** session A and remove the external link; save. Confirm the control becomes **disabled** with tooltip without needing to switch sessions.
3. With session B selected, **edit** session B and add an external link; save. Confirm the control becomes **enabled** next to the title.

---

## Edge cases (optional)

- **Empty or whitespace-only external link**: If the backend or form allows saving a value that is only spaces, the control should be **disabled** with the same tooltip (e.g. "No external link provided").
- **Invalid or unreachable URL**: When enabled, activate the control with an invalid URL (e.g. `http://invalid.example`). The browser should handle the failure (e.g. error page); the app should not crash and should stay in the current tab.
