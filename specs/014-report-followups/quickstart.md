# Quickstart: Report Follow-Up Improvements

**Branch**: `014-report-followups`  
**Date**: 2026-03-29

Minimal steps to validate the new report follow-ups end to end.

---

## Prerequisites

- Backend running at `http://localhost:8000`
- Frontend dev server running from `frontend/`
- At least one session with uploaded logs
- LLM configuration available so report generation can complete

---

## 1. Generate a report with a recognizable incident question

1. Open the app and select a session with uploaded logs.
2. Generate a report with a distinctive question, for example:

```text
Why did checkout requests start timing out after the deploy?
```

3. Wait for the report to finish generating and appear in the report viewport.

Expected results:

- A new report appears in history.
- The full report contains a `Coding agent fix prompt` section.

---

## 2. Validate report history context

1. Open the report history list for the active session.
2. Confirm the new report row shows a short preview of the incident question.
3. Confirm the list remains readable and does not show the coding-agent fix prompt inline.
4. Open the report and confirm the full incident question is available on demand.

Expected results:

- History rows are distinguishable by question preview.
- Legacy or missing-question rows do not break layout.

---

## 3. Validate the report copy control

1. Open a generated report in the viewport.
2. Use the compact copy button near the rendered report content.
3. Paste into a Markdown-capable destination such as a text editor or issue draft.

Expected results:

- Paste result includes headings, ordered lists, and fenced code blocks as Markdown.
- Success toast appears on successful copy.
- If clipboard access is denied, the app shows a clear failure message.

---

## 4. Validate PDF and Markdown export

1. Export the same report as Markdown.
2. Open the downloaded `.md` file and confirm the `Coding agent fix prompt` section is present.
3. Export the same report as PDF.
4. Open the PDF and confirm:
   - major report sections are present and readable
   - the incident report structure is intact
   - troubleshooting steps remain ordered
   - long question text and code blocks do not break layout

Expected results:

- Markdown export mirrors the report content.
- PDF export completes successfully for normal reports.

### PDF fixture matrix for SC-004

Use this matrix for representative PDF-export validation:

| Fixture | Focus | Expected Result |
|--------|-------|-----------------|
| Short structured report | Basic section rendering | PDF exports successfully and includes all major headings |
| Long incident question | Long inline text wrapping | Question context remains readable without layout breakage |
| Mixed prose and code blocks | Markdown variety | Code blocks and prose remain readable and ordered steps stay numbered |

### Current automated fixture snapshot

| Fixture | Result | Source |
|--------|--------|--------|
| Short structured report | PASS | `backend/tests/unit/test_export.py` |
| Long incident question | PASS | `backend/tests/unit/test_export.py` |
| Mixed prose and code blocks | PASS | `backend/tests/unit/test_export.py` |

Current automated fixture pass rate: `3/3` (100%). Manual export checks are still recommended before release.

---

## 5. Validate failure handling

1. Attempt PDF export with content unavailable, or simulate a backend/export failure.
2. Attempt to use the copy button in an environment where clipboard write is blocked.

Expected results:

- Export failure is surfaced clearly and not presented as success.
- Copy failure is surfaced clearly and not silent.

---

## 6. Recommended automated checks

```bash
cd /Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend && pnpm test:run
cd /Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend && pytest
```

Recommended test focus:

- report history metadata rendering
- report viewport copy success/failure
- report API schema with question metadata
- PDF export fixtures covering long text, code blocks, and ordered lists
