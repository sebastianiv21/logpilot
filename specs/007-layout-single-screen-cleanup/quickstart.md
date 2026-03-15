# Quickstart: Single-Screen Layout, Pagination, and Copy Cleanup

**Branch**: 007-layout-single-screen-cleanup  
**Date**: 2026-03-15  

Minimal steps to run and validate layout, pagination, Back to Home placement, top-bar home link and icon, copy/icon cleanup, and upload summary charts. Assumes the full stack (backend and frontend) is running per project docs.

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`).
- **Frontend** dev server running (e.g. `cd frontend && pnpm dev`).
- **Viewport**: Use a typical desktop size (e.g. ≥1280×720) to validate single-screen layout.

---

## 1. Validate single-screen layout and right-side space

1. Open the app at `/` and select or create a session.
2. Confirm the **main content** (Upload logs, Logs & metrics, Reports) and **Sessions** sidebar fit on **one screen** without vertical scroll at 1280×720 or larger.
3. Confirm **space on the right** is used (e.g. sections arranged in a grid or two columns) so that key areas are visible at a glance.
4. Shrink the window; confirm that if content no longer fits, **scrolling** is used (no collapsible sections).

---

## 2. Validate sessions list pagination

1. With **multiple sessions** (create several if needed), open the **Sessions** sidebar.
2. Confirm sessions are shown in **batches of 10** with a **"Load more"** control.
3. Click **Load more**; confirm the next batch appears.
4. If available, confirm **Previous** (or back-to-start) returns to the previous batch or first batch.

---

## 3. Validate KB search pagination

1. Navigate to the **knowledge** page (e.g. `/knowledge`).
2. Run a **search** that returns enough results to span more than one batch.
3. Confirm results are shown in **batches of 10** with **Load more** (and optional **Previous**).

---

## 4. Validate Back to Home inside knowledge space

1. On the **knowledge** page, confirm **"Back to Home"** (or equivalent) is **inside** the main content area (e.g. above or beside the Knowledge base and Search sections), **not** in the global top navigation bar.
2. Click it; confirm navigation to `/` (home/session view).

---

## 5. Validate top bar: home link and app icon

1. From any view (home or knowledge), confirm **"LogPilot"** in the **top bar** is **clickable** and navigates to `/` when clicked.
2. Confirm an **application icon** (e.g. logs-related, Lucide) is visible **next to or with** "LogPilot" in the top bar.

---

## 6. Validate upload/processing summary charts

1. On the **home** page with a session selected, **upload** a .zip log archive.
2. After success or partial completion, confirm the **upload summary** (files processed, skipped, lines parsed, rejected, parsed coverage) is presented **visually** (e.g. bar charts, donut, or progress bar) in addition to or instead of a plain bullet list.
3. Confirm the visualization is readable and matches the numeric values.

---

## 7. Validate copy and icon deduplication

1. On the **knowledge** page, confirm there is no **redundant** heading (e.g. "Knowledge base" not repeated as title and identical subheading).
2. On the **home** page, confirm **Upload logs** and **Generate report** use **distinct icons** (e.g. Upload vs FileOutput/Sparkles), not the same icon for both actions.

---

## Optional: accessibility

1. Use **keyboard only**: Tab to Load more, Previous, Back to Home, and LogPilot link; activate and confirm behavior.
2. Confirm chart summary has labels or text alternative for key values.
