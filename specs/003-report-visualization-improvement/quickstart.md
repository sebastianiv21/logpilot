# Quickstart: Report Visualization Improvement

**Branch**: `003-report-visualization-improvement`  
**Date**: 2026-03-14  

Minimal steps to run and validate report visualization changes. Assumes the full stack (backend, frontend, and optional Docker Compose services) is already running per [002-frontend-implementation quickstart](../002-frontend-implementation/quickstart.md).

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`).
- **Frontend** dev server running (e.g. `cd frontend && pnpm dev`).
- At least one **session** with logs (and optionally knowledge ingested) so report generation can produce a report with sections.

---

## 1. Generate a report

1. Open the app and select a session that has logs (and optionally run knowledge ingest).
2. Go to the report / generate flow and submit an incident question (e.g. "Why did errors spike?").
3. Wait until the report has content (polling finishes and the report body is visible).

---

## 2. Validate in-browser view

1. Open the generated report in the app.
2. **Hierarchy**: Confirm section headings (Incident Summary, Possible Root Cause, Uncertainty, Supporting Evidence, Recommended Fix, Next troubleshooting steps) are visually distinct and ordered.
3. **Next troubleshooting steps**: Confirm this section is rendered as a **numbered list** (1., 2., 3., …), not bullets.
4. **Lists**: Confirm other sections that contain lists show clear bullet or numbered formatting with consistent spacing.
5. **Code**: If the report contains code blocks or inline code, confirm they are visually distinct (e.g. monospace, background).
6. **Long lines**: If the report contains long URLs or log lines, confirm they wrap and do not force horizontal scrolling.
7. **Zoom**: Increase browser zoom (e.g. 150–200%); confirm layout remains readable and no overlapping (FR-008).

---

## 3. Validate Markdown export

1. Click **Export Markdown** and open the downloaded `.md` file in a text editor or a Markdown viewer (e.g. GitHub preview, VS Code).
2. Confirm headings, paragraphs, and lists are valid Markdown.
3. Confirm **Next troubleshooting steps** appears as a numbered list (e.g. `1. ...`, `2. ...`) in the file and, if applicable, in the viewer’s rendered view.

---

## 4. Validate PDF export

1. Click **Export PDF** and open the downloaded PDF in a standard reader.
2. Confirm section hierarchy (headings and body text) is clear and readable.
3. Confirm **Next troubleshooting steps** appear as a numbered list (1., 2., 3., …), not bullets.
4. Confirm code or preformatted blocks are distinguishable from body text.
5. At 100% zoom (and, if possible, when printed on A4/Letter), confirm no text is cut off or overlapping.

---

## 5. Validate export failure handling

1. (Optional) Simulate failure: e.g. stop the backend, then try **Export PDF** or **Export Markdown**.
2. Confirm the user sees a **clear, user-friendly error message** (e.g. "Export failed" or similar), not a raw stack trace or technical message (FR-009).

---

## 6. Run tests (when available)

From repo root or feature areas:

- **Frontend**: `cd frontend && pnpm test` (or `npm run test`).
- **Backend**: `cd backend && pytest` (or `uv run pytest`).

Add or run unit tests for export (e.g. PDF list numbering) and report view styling as the implementation adds them.
