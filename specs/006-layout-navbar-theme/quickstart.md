# Quickstart: App layout and navigation improvements

**Branch**: `006-layout-navbar-theme`  
**Date**: 2026-03-15  

Minimal steps to run and validate theme switcher, sidebar visibility, copy changes, and LogPilot in the top bar. Assumes the full stack (backend and frontend) is running per project docs.

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`).
- **Frontend** dev server running (e.g. `cd frontend && pnpm dev`).

---

## 1. Validate theme switcher

1. Open the app (e.g. at `/`).
2. Confirm the **top bar** has a **theme control** as the **last item** (right side). It toggles between two states (e.g. sun/moon).
3. Click the theme control; confirm the **theme changes immediately** (e.g. light ↔ dark).
4. **Reload** the page; confirm the **same theme** is still applied (persistence).
5. Clear localStorage for the app origin (or remove key `theme`), reload; confirm **default** is system preference (e.g. dark in OS dark mode, light in OS light mode), or **light** if system preference is unavailable.

---

## 2. Validate sidebar hidden on knowledge page

1. Navigate to the **knowledge page** (e.g. via the database icon in the top bar or direct URL `/knowledge`).
2. Confirm the **left sidebar** (sessions list and create-session controls) is **not visible**. Only the top bar and main content (KB ingestion and search) are visible.
3. Use "Back to home" (or equivalent) to return to `/`; confirm the **left sidebar is visible again** with the sessions list.
4. Confirm **skip-to-main-content** and keyboard focus order still work when the sidebar is hidden.

---

## 3. Validate copy and instructional line

1. On the **home** page, confirm the phrase **"Upload logs or switch session in the sidebar."** does **not** appear anywhere.
2. With **no session selected**, confirm **one short instructional line** is shown (e.g. "Select or create a session to get started.").
3. Select or create a session; confirm the rest of the home content (Upload logs, Logs & metrics, Reports) is unchanged.

---

## 4. Validate LogPilot in top bar only

1. On the **home** page, confirm **"LogPilot"** appears in the **top bar** (e.g. left side of the navbar).
2. Confirm **"LogPilot"** does **not** appear in the **left sidebar** (sidebar shows only Sessions and session-related controls).
3. Confirm the **main content** of the home page does **not** use "LogPilot" as the **primary page heading** (branding is in the top bar only).
4. On the **knowledge** page (sidebar hidden), confirm **"LogPilot"** is still visible in the **top bar**.

---

## 5. Optional: accessibility

1. Use **keyboard only**: Tab to the theme switcher, activate (Enter/Space); confirm theme toggles. Tab to "Back to home" on the knowledge page; confirm navigation.
2. Confirm theme switcher and LogPilot are announced appropriately (e.g. aria-label or title).
