# Quickstart: Scrollable Session List and Dynamic Session Titles with Copy ID

**Branch**: 008-scrollable-session-list-titles  
**Date**: 2026-03-15  

Minimal steps to run and validate the scrollable session list, dynamic section titles, and session ID copy. Assumes the full stack (backend and frontend) is running per project docs.

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`).
- **Frontend** dev server running (e.g. `cd frontend && pnpm dev`).
- At least **one session** (create via "+ Create session" if needed). For scroll behavior, create enough sessions so the list exceeds the sidebar height.

---

## 1. Validate self-contained scrollable session list

1. Open the app at `/` and ensure the **Sessions** sidebar is visible (not on the knowledge page).
2. If the session list has **more items than fit** in the sidebar:
   - Scroll **inside** the session list area (use the scrollbar in the sidebar list).
   - Confirm the **main content** (Upload logs, Logs & metrics, Reports) **does not move**; only the session list scrolls.
3. If the list has **few items**:
   - Confirm the list area does not force the whole page to scroll; layout remains stable.

---

## 2. Validate dynamic section titles (Logs & metrics and Reports)

1. **Session with a name**: Create or edit a session to give it a name (e.g. "Incident #123"). Select it. Confirm both **Logs & metrics** and **Reports** section titles show that name.
2. **Session without a name**: Select a session that has no name. Confirm both section titles show **"Session "** followed by the first 8 characters of the ID (e.g. "Session f4bee7b1").
3. **No session**: Clear or ensure no session is selected (if the UI allows). Confirm both sections show a placeholder title (e.g. "No session selected").
4. **Switch session**: Change the current session; confirm section titles update immediately to the new session’s name or "Session xxxxxxxx".

---

## 3. Validate long session name (truncate + tooltip)

1. Set a session name that is **very long** (e.g. 50+ characters). Select that session.
2. Confirm the section title is **truncated with an ellipsis**.
3. **Hover** over the title; confirm the **full name** appears (e.g. in a tooltip or browser `title`).

---

## 4. Validate session ID line and copy

1. Select a session. Below the **Logs & metrics** and **Reports** section titles, confirm the **full session ID** is shown with a **copy icon/button** next to it.
2. Click the **copy** control. Confirm a **success** message (e.g. toast "Session ID copied").
3. Paste elsewhere (e.g. notepad); confirm the pasted value is the **full session ID**.
4. (Optional) If possible, simulate clipboard failure (e.g. browser permission denied); confirm a **failure** toast (e.g. "Copy failed" or "Couldn't copy").
5. With **no session** selected, confirm the session ID line and copy control are **hidden**.

---

## 5. Validate accessibility (copy control)

1. Focus the **copy** button (keyboard tab). Confirm it has a visible focus style.
2. Activate with **Enter** or **Space**; confirm copy and toast still work.
3. If using a screen reader, confirm the button has an **accessible name** (e.g. "Copy session ID").

---

## 6. Re-check after implementation

- Section titles and session ID line update on session change without page reload.
- Session list scroll does not scroll the main content.
- Placeholder and hidden ID/copy when no session; truncation and copy feedback as above.
