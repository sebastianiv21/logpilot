# Quickstart: Knowledge base config route and layout

**Branch**: `005-kb-config-route-layout`  
**Date**: 2026-03-15  

Minimal steps to run and validate the KB route and header control. Assumes the full stack (backend and frontend) is running per project docs (e.g. backend at `http://localhost:8000`, frontend dev server).

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`).
- **Frontend** dev server running (e.g. `cd frontend && pnpm dev`).

---

## 1. Validate upper-right control and tooltip

1. Open the app at the home page (`/`).
2. Confirm the **upper-right** area of the main content shows a **database icon** with a **status indicator** (colored dot). No visible text label.
3. Hover (or focus) the control; confirm a **tooltip** shows **"Knowledge base"**.
4. Confirm **indicator color**: red when no ingest has completed or last run failed; green when ingest has completed successfully; yellow/ochre with **pulsating** effect when ingestion is in progress (start ingest from the knowledge page to test).

---

## 2. Validate navigation to knowledge page

1. Click the upper-right control (database icon). Confirm navigation to the **knowledge base page** (e.g. `/knowledge`).
2. Confirm the page shows **knowledge base ingestion** and **knowledge search** only, grouped under a clear heading.
3. Confirm a visible **return** control (e.g. "Back to home" or "Home") that navigates back to `/`.
4. Use browser back from the knowledge page; confirm you return to the previous screen.

---

## 3. Validate main screen without KB block

1. On the **home** page (`/`), confirm the knowledge base block (ingestion + search) is **not** present.
2. Confirm sections appear in order: intro, Upload logs, Logs & metrics, Reports — with clear headings and spacing.

---

## 4. Validate direct URL and accessibility

1. Open `/knowledge` directly (e.g. in a new tab or via address bar). Confirm the knowledge page loads and is usable (no session required).
2. Use **keyboard only**: Tab to the upper-right control, activate it (Enter/Space), confirm navigation to knowledge page. Confirm the control is announced as "Knowledge base" (screen reader or dev tools).

---

## 5. Optional: layout hierarchy

1. Scan the main and knowledge pages; confirm section headings and spacing make "session work" vs "knowledge base" clearly distinguishable.
