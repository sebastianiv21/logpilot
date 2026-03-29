# Data Model: Report Follow-Up Improvements

**Branch**: `014-report-followups`  
**Date**: 2026-03-29  
**Source**: Feature spec, clarified decisions, and existing report/session models.

---

## 1. Report (persisted entity)

The existing `Report` entity gains source-question metadata while remaining the canonical store for generated report content.

| Field | Type | Required | Notes |
|------|------|----------|-------|
| `id` | string | Yes | Stable report identifier |
| `session_id` | string | Yes | Parent session identifier |
| `content` | string | Yes | Full generated report in Markdown |
| `question` | string | Yes | Original incident question submitted for this report run |
| `created_at` | string | Yes | ISO 8601 timestamp |

**Validation rules**

- `question` must be non-empty trimmed text when a report is created.
- `content` may be temporarily empty while generation is in progress, but the record still retains `question`.
- Existing databases without `question` must be migrated additively so older rows remain readable.

**Lifecycle**

1. User submits an incident question.
2. Backend creates a report record with `question` stored and empty `content`.
3. Background generation fills `content`.
4. UI renders report history from persisted report metadata and renders full report detail from the completed record.

---

## 2. Report history item (API/view model)

Report history uses a list-oriented projection of the report record.

| Field | Type | Required | Notes |
|------|------|----------|-------|
| `id` | string | Yes | Report identifier |
| `session_id` | string | Yes | Parent session |
| `created_at` | string | Yes | Creation timestamp |
| `question_preview` | string | No | Short preview derived from `question` for list scanability |
| `has_question` | boolean | Yes | Indicates whether question metadata exists for the row |

**Validation rules**

- `question_preview` is derived from `question` and should be short enough for list rendering.
- `has_question=false` covers legacy rows created before the new field existed or rows with unavailable question metadata.
- History items must not include the coding-agent fix prompt.

---

## 3. Report detail payload (API/view model)

The detail view expands a report history item with the full question and full Markdown report.

| Field | Type | Required | Notes |
|------|------|----------|-------|
| `id` | string | Yes | Report identifier |
| `session_id` | string | Yes | Parent session |
| `created_at` | string | Yes | Creation timestamp |
| `question` | string | No | Full incident question for on-demand display |
| `content` | string | Yes | Full report Markdown |

**Validation rules**

- `question` should be returned when available and omitted or null-safe for legacy rows.
- `content` remains the source of truth for viewport rendering, Markdown copy, and export.

---

## 4. Report content structure (logical model)

The report Markdown now includes an expanded section contract for full-report views and exports.

Required logical sections:

1. `Incident Summary`
2. `Possible Root Cause`
3. `Uncertainty`
4. `Supporting Evidence`
5. `Recommended Fix`
6. `Coding agent fix prompt`
7. `Next troubleshooting steps`

**Rules**

- `Coding agent fix prompt` appears only in the full generated report and its exports.
- `Next troubleshooting steps` remains an ordered Markdown list.
- The full report Markdown is the source for both viewport copy and exported Markdown/PDF.

---

## 5. Derived behaviors

- **Clipboard payload**: exact Markdown content from `Report.content`.
- **Question preview**: derived display text from `Report.question`; truncation/presentation is a view concern, but the preview contract should be stable enough for history rendering.
- **PDF export**: derived binary representation of `Report.content`, expected to preserve section order and readable structure.
