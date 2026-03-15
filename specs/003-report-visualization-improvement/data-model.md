# Data Model: Report Visualization Improvement

**Branch**: `003-report-visualization-improvement`  
**Date**: 2026-03-14  
**Source**: Feature spec and existing report entity. No new persistence or API schema; this document describes presentation constraints applied to the existing Report content.

---

## 1. Report (unchanged)

The **Report** entity is unchanged from the existing backend/frontend model:

| Field        | Type   | Notes                                  |
|-------------|--------|----------------------------------------|
| id          | string | Unique identifier                      |
| session_id  | string | Parent session                         |
| content     | string | Markdown body of the report             |
| created_at  | string | ISO 8601 datetime                      |

**Validation**: Unchanged. Content is free-form Markdown produced by the agent.

**State**: Unchanged. Reports are created by report generation and read/exported by the UI.

---

## 2. Presentation constraints (no new fields)

The feature does not add new attributes to Report. Instead, the following rules apply when **interpreting and rendering** `content`:

- **Sections**: Content is expected to contain the standard sections (Incident Summary, Possible Root Cause, Uncertainty, Supporting Evidence, Recommended Fix, Next troubleshooting steps). These are identified by Markdown headings (e.g. `## Next troubleshooting steps`). No schema enforces presence or order; the agent prompt and existing contract define them.
- **List style**: The "Next troubleshooting steps" section MUST be rendered and exported as a **numbered list** (1., 2., 3., …). All other sections MAY be bullet or numbered lists as appropriate; no single style is mandated for them.
- **Code and long lines**: Content may include fenced code blocks and long lines (URLs, log lines). Rendering MUST distinguish code from prose and MUST wrap long lines so layout does not break (FR-006, FR-007).

These constraints are enforced by (1) agent prompt (output format), (2) optional content normalizer (if implemented), (3) frontend renderer (ReactMarkdown + styles), and (4) backend export (Markdown passthrough, PDF with ol/ul distinction). No new entities or tables.
