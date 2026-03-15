# Contract: Report Content Format (Markdown)

**Branch**: `003-report-visualization-improvement`  
**Date**: 2026-03-14  
**Purpose**: Define the expected structure and formatting of report `content` (Markdown) so that in-app view and export (Markdown/PDF) can render it consistently and meet FR-002, FR-003, FR-004, FR-005.

---

## Scope

This contract applies to the **content** field of the Report entity returned by `GET /sessions/{session_id}/reports/{report_id}` and used as input to the export endpoint. It does not change the API schema; it constrains how the agent produces content and how consumers (frontend, export pipeline) interpret it.

---

## Required sections

Reports are expected to contain the following sections as Markdown headings (level 2, e.g. `## Section Name`). Order and presence may vary; the agent prompt defines them.

- Incident Summary  
- Possible Root Cause  
- Uncertainty  
- Supporting Evidence  
- Recommended Fix  
- Next troubleshooting steps  

---

## List formatting

- **Next troubleshooting steps**: MUST be emitted and rendered as a **numbered list**. In Markdown this is `1. First step`, `2. Second step`, etc. In the in-app view and in exported Markdown and PDF, this section MUST appear as an ordered list (1., 2., 3., …).  
- **All other sections**: MAY use bullet lists (`-` or `*`) or numbered lists as appropriate; no single style is mandated.

---

## Other formatting

- **Code or preformatted text**: Fenced code blocks (```) or inline `code` are allowed and MUST be rendered distinctly from prose (e.g. monospace, background) in browser and exports.  
- **Long lines**: Content may contain long lines (URLs, log excerpts). Consumers MUST wrap or constrain them so that layout does not break (no mandatory horizontal scroll for normal reading).

---

## Export behavior

- **Markdown export**: Returns the report content as `text/markdown` with the same structure and list formatting (troubleshooting steps numbered).  
- **PDF export**: Renders the same content with clear section hierarchy and list formatting; ordered lists in the source MUST appear as numbered items in the PDF, not as bullets.

---

## Error handling

When export fails (e.g. server error, PDF generation failure), the user MUST see a clear, user-friendly error message (FR-009). Backend may return an appropriate HTTP status and `detail`; frontend must surface a non-technical message when possible.
