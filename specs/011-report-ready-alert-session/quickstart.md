# Quickstart: Report-Ready Alert Session Context and View Report

**Branch**: 011-report-ready-alert-session  
**Date**: 2026-03-15  

Minimal steps to run and validate report-ready toast session identity and "View report" action. Assumes backend and frontend are running per project docs.

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`) with sessions and report generation (existing).
- **Frontend** dev server running (e.g. `cd frontend && pnpm dev`).

---

## 1. Toast always shows session identity (P1)

1. Select a session that has a **custom name** (or create one and set a name). Start **report generation** for that session; wait for the report to become ready (or trigger in another session and switch back).
2. When the report-ready toast appears, confirm the message includes the **session name** (e.g. “Report ready (My Session)” or similar). It must NOT show only “Report ready” with no session context.
3. Select a session with **no custom name** (or use session ID only). Generate a report and wait for ready. Confirm the toast shows a **session identifier** (e.g. truncated session ID) so you can tell which session the report belongs to.
4. Optionally: have **multiple sessions** with reports generating; when one becomes ready, confirm the toast for that one clearly identifies its session.

---

## 2. “View report” opens session and report (P2)

1. From any screen (e.g. another session or Knowledge page), ensure a report is **generating** for a given session (or trigger one and wait for ready).
2. When the **report-ready toast** appears, click the **“View report”** button (or link) in the toast.
3. Confirm the app **switches to that session** and **opens that report** (e.g. report modal or view) so you see the report content immediately without manually selecting the session or the report from the list.
4. If you are **already viewing that session** (and optionally that report), click “View report” again; confirm the app brings the report into view or keeps it in view without confusing navigation.

---

## 3. Keyboard and screen reader (FR-005, SC-005)

1. Trigger a report-ready toast. Use **keyboard only** (Tab to focus the “View report” control, Enter/Space to activate). Confirm the same navigation and report open occurs as with a mouse click.
2. With a **screen reader** enabled, trigger the toast and locate the “View report” control. Confirm it has an **accessible name** (e.g. “View report”) and that activating it opens the session and report.

---

## 4. Fallback when session name unavailable (FR-001)

1. If possible, simulate a **network failure** or delay when the report becomes ready (e.g. disconnect briefly, or use a session that the backend cannot resolve). Confirm the toast still shows a **session identifier** (e.g. truncated ID) and does NOT show only “Report ready” with no context. Confirm “View report” still works (uses known session/report IDs).

---

## 5. Session or report no longer available (FR-003, SC-003)

1. Trigger a report-ready toast, then **delete that session** (or otherwise make it unavailable) before clicking “View report.” Click **“View report.”** Confirm the app shows a **clear message** (e.g. toast or inline) and does NOT show a broken or blank view.
2. If the app supports deleting or hiding a single report, make the report unavailable after the toast, then click “View report.” Confirm a clear indication and no invalid navigation.

---

## Edge cases (optional)

- **Multiple reports ready in quick succession**: Trigger two reports (different sessions) to become ready close together. Confirm each toast identifies its session and has its own “View report” that takes you to the correct report.
- **Very long session name**: Use a session with a very long name; confirm the toast message remains readable (e.g. truncated) and full name available on hover or after opening the report.
