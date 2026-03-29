# Contract: Report History and Export Follow-Ups

**Branch**: `014-report-followups`  
**Date**: 2026-03-29  
**Purpose**: Define the API and UI-facing contract for report history metadata, full report content, Markdown copy behavior, and PDF export expectations.

---

## Scope

This contract covers:

- `POST /sessions/{session_id}/reports/generate`
- `GET /sessions/{session_id}/reports`
- `GET /sessions/{session_id}/reports/{report_id}`
- `GET /sessions/{session_id}/reports/{report_id}/export?format=markdown|pdf`
- The in-app report viewport copy interaction

It does not change session APIs or add a new export format.

---

## 1. Generate report request/response

### Request

`POST /sessions/{session_id}/reports/generate`

```json
{
  "question": "Why did checkout requests start timing out after the deploy?"
}
```

### Response

Returns `202 Accepted` and creates a report record that already stores the incident question, even before report content is ready.

```json
{
  "id": "report-uuid",
  "session_id": "session-uuid",
  "created_at": "2026-03-29T12:34:56Z",
  "content": null
}
```

---

## 2. Report history list response

`GET /sessions/{session_id}/reports`

Returns history rows suitable for list rendering and scanability.

```json
{
  "reports": [
    {
      "id": "report-uuid",
      "session_id": "session-uuid",
      "created_at": "2026-03-29T12:34:56Z",
      "question_preview": "Why did checkout requests start timing out after the deploy?",
      "has_question": true
    }
  ]
}
```

### Rules

- `question_preview` is a short, readable preview for the history list.
- `has_question=false` indicates legacy rows or missing question metadata.
- The list response MUST NOT include the coding-agent fix prompt or full report Markdown.

---

## 3. Report detail response

`GET /sessions/{session_id}/reports/{report_id}`

Returns the full report payload used for viewport rendering, Markdown copy, and export readiness checks.

```json
{
  "id": "report-uuid",
  "session_id": "session-uuid",
  "created_at": "2026-03-29T12:34:56Z",
  "question": "Why did checkout requests start timing out after the deploy?",
  "content": "## Incident Summary\n...\n## Next troubleshooting steps\n1. ...\n## Coding agent fix prompt\n..."
}
```

### Rules

- `question` contains the full stored incident question when available.
- `content` is Markdown and remains the source of truth for rendered report content.
- Full report content MUST include the `Coding agent fix prompt` section when generation succeeds.

---

## 4. Report Markdown content contract

Full-report Markdown must preserve these sections for viewport rendering and exports:

- `Incident Summary`
- `Possible Root Cause`
- `Uncertainty`
- `Supporting Evidence`
- `Recommended Fix`
- `Next troubleshooting steps`
- `Coding agent fix prompt`

### Additional rules

- `Next troubleshooting steps` MUST remain an ordered Markdown list.
- `Coding agent fix prompt` MUST appear only in full-report surfaces, not in report-history rows, and it MUST be the final section.
- Markdown copy uses this exact content, not a separate transformed representation.

---

## 5. Copy interaction contract

From the rendered report viewport:

- User activates a compact copy control.
- The app copies the report Markdown from `content` to the clipboard.
- Success feedback is shown when the clipboard write succeeds.
- Failure feedback is shown when clipboard access fails or is unavailable.

The control should align with the compact session-ID copy pattern in the current UI.

---

## 6. Export contract

### Markdown export

- Returns `text/markdown`.
- Must preserve the same full-report Markdown structure, including `Coding agent fix prompt`.

### PDF export

- Returns `application/pdf` on success.
- Must render the major report sections in readable order.
- Must handle long question text, ordered troubleshooting steps, prose, and code blocks without truncating or hanging for normal report sizes.
- On failure, the endpoint returns a clear error response and the frontend must present that failure clearly.

---

## 7. Failure states

- `404 Not Found`: report or session does not exist.
- `409 Conflict`: report content is not ready for export.
- `503 Service Unavailable`: PDF export fails or report generation is unavailable.

User-visible handling must remain clear and non-misleading, especially for export and clipboard failures.
