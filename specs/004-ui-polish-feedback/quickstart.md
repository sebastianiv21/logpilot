# Quickstart: UI polish — icons, copy, loading cues, report-ready feedback

**Branch**: `004-ui-polish-feedback`  
**Date**: 2026-03-15  

Minimal steps to run and validate UI polish changes. Assumes the full stack (backend and frontend) is running per [002-frontend-implementation quickstart](../002-frontend-implementation/quickstart.md).

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`).
- **Frontend** dev server running (e.g. `cd frontend && npm run dev`).
- At least one **session** (optional: with logs and/or knowledge ingested) for report generation.

---

## 1. Validate loading indicators

1. Open the app. While sessions load, confirm a **visual** loading indicator (e.g. spinner or skeleton) in addition to or instead of plain "Loading…" text.
2. Open a report or the reports list; confirm loading state is visually clear.
3. Start **Upload logs** or **Start ingestion** (knowledge) or **Generate report**; confirm the button or area shows a visible busy state (e.g. spinner) while the action is in progress.

---

## 2. Validate report-ready toast and sound

1. Select a session that has logs (and optionally run knowledge ingest).
2. Go to **Generate report** and submit an incident question (e.g. "Why did errors spike?").
3. Wait for the report to finish generating (or switch session/tab and wait).
4. **Then**: A **toast** should appear (e.g. "Report ready" or "Report ready (Session X)" when multiple sessions have reports generating).
5. A **short, subtle sound** should play once (if browser allows and sound is not muted). If multiple reports become ready in quick succession, only one sound should play at a time (throttled/queued).
6. Confirm that the toast appears even when you are not on the report view (background notification).

---

## 3. Validate icons

1. Browse: **Sessions** (sidebar), **Reports**, **Log search**, **Knowledge search**, **Upload logs**, **Generate report**.
2. Confirm **icons** appear on key actions or section headings where they aid recognition (e.g. upload, export, generate, search), and that icons are **not** on every label or every button (moderate density).

---

## 4. Validate copy

1. Review headings, buttons, placeholders, and error/empty messages across the main app.
2. Confirm text is **concise and consistent** (e.g. short button labels, non-technical error messages like "Check your connection" where appropriate).
3. Confirm loading/status text is consistent (e.g. "Loading…" vs "Loading report…" used deliberately).

---

## 5. Run tests (optional)

From repo root or `frontend/`:

```bash
cd frontend && npm run test:run
```

Fix any failing tests related to new loading UI, toasts, or copy changes.
