# Quickstart: Upload State Scoped Per Session and Persistent Across Refresh

**Branch**: 010-upload-session-state-fix  
**Date**: 2026-03-15  

Minimal steps to run and validate session-scoped upload result display and state persistence after refresh. Assumes backend and frontend are running per project docs.

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`) with new GET `/sessions/{session_id}/upload-summary` and persistence of last upload result.
- **Frontend** dev server running (e.g. `cd frontend && pnpm dev`).

---

## 1. Validate upload result scoped to current session (P1)

1. Create or select **Session A**, upload a .zip log file, and confirm the **upload summary** (success/partial/failed, counts, charts) is shown for Session A.
2. **Switch to Session B** (different session). Confirm the upload summary area shows **only** Session B’s result (or is **empty** if B has no upload). Session A’s result must **not** be shown.
3. **Switch back to Session A**. Confirm Session A’s upload summary is shown again (not B’s).
4. Optionally: upload for Session B; confirm the summary updates to B’s result while B is selected; switching to A shows A’s result only.

---

## 2. Validate state survives refresh and last summary shown (P2)

1. With at least one session that has logs (e.g. Session A from step 1), **refresh the page** (F5 or full reload).
2. **Select the same session** (A). Confirm:
   - A **loading indicator** (e.g. spinner or skeleton) appears briefly while session state is fetched.
   - After load, the app shows that the session **has logs** (e.g. log search or related UI is available).
   - The **last upload summary** (counts, charts) for that session is shown again **without** re-uploading.
3. Select a session that **has never had logs** uploaded. Confirm the upload area does **not** show a summary from another session and does not show "has logs".

---

## 3. Validate loading and error + retry (FR-006, FR-007)

1. **Loading**: During step 2, confirm a **loading indicator** is shown while "has logs" and last upload summary are being fetched; no other session’s result is shown during load.
2. **Error + retry**: Simulate a failure (e.g. stop the backend, refresh, select a session that has logs). Confirm an **error message** is shown and a **retry** control (e.g. button or link) is available. Click **retry** (backend must be back up). Confirm retry applies **only to the selected session** (not a full reload of all sessions).
3. **Success after retry**: After a successful retry, confirm the **loaded state** (upload summary or empty) is shown and a **brief success message** (e.g. toast or inline "Loaded") appears.

---

## 4. Edge cases

1. **Upload in progress**: Start an upload for Session A, then switch to Session B before it completes. Confirm the in-progress state remains tied to A; after completion, the result is shown only when A is selected again.
2. **Session with no backend data**: If the backend no longer has data for a session (e.g. session or logs removed), after refresh the app should reflect that (no stale "has logs" or summary for that session).

---

## Optional: API check

- `GET /sessions/{session_id}/upload-summary` returns 200 with last result or 404 when session not found or no upload yet. After POST upload, a subsequent GET for that session returns the same summary payload.
- To validate the API automatically: run `./validate-api.sh` (or `./validate-api.sh http://localhost:8000`) from this spec directory with the backend up.
