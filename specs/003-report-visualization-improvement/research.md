# Research: Report Visualization Improvement

**Branch**: `003-report-visualization-improvement`  
**Date**: 2026-03-14  
**Goal**: Resolve technical choices for in-browser report styling, numbered troubleshooting steps, Markdown/PDF export quality, and baseline accessibility. No NEEDS CLARIFICATION remained; decisions below are driven by the spec and existing codebase.

---

## 1. Numbered "Next troubleshooting steps" (source of truth)

**Decision**: **Agent prompt is the source of truth.** Update the system prompt in `backend/app/services/agent.py` to require that the "Next troubleshooting steps" section be output as a Markdown numbered list (e.g. `1. First step`, `2. Second step`). Optionally, add a small normalizer (backend or shared) that, when generating Markdown for display/export, ensures the "Next troubleshooting steps" section uses `1.` … `2.` … if the agent ever outputs bullets there; this is a robustness fallback, not a substitute for the prompt.

**Rationale**: The spec requires that section to be a numbered list everywhere (browser, Markdown export, PDF). Having the agent emit correct Markdown keeps a single source of truth and avoids fragile regex over arbitrary content. A normalizer can fix occasional model drift without changing product behavior.

**Alternatives considered**: Relying only on post-processing to convert bullets to numbers in that section was rejected because it can misformat nested or multi-line steps; prompt-first is more reliable. No change to agent tools or schema.

---

## 2. PDF export: ordered vs unordered lists

**Decision**: **Parse the HTML produced from Markdown and distinguish `<ol>` vs `<ul>`.** The current `export_pdf` uses a regex that extracts `<li>` content but treats every list item as a bullet (`•`). The Python `markdown` library with extension `extra` produces `<ol><li>...</li></ol>` for numbered lists and `<ul><li>...</li></ul>` for bullet lists. Use an HTML parser (e.g. `html.parser.HTMLParser` or a minimal tree walk) to emit a stream of block-level elements that includes, for each `<li>`, whether it belongs to an `<ol>` and its 1-based index. In ReportLab flowables, render `<ol>` items as `"1. text"`, `"2. text"`, etc., and `<ul>` items as `"• text"`.

**Rationale**: ReportLab does not render HTML; we already convert Markdown → HTML → flowables. The only missing piece is preserving list type and order. A small parser keeps dependencies minimal (stdlib `html.parser` is sufficient) and satisfies FR-003/FR-005 for PDF.

**Alternatives considered**: (1) Regex to detect `<ol>` and count `<li>` until `</ol>` — rejected due to nested lists and malformed output. (2) Client-side PDF generation (e.g. jsPDF) — rejected to keep export on the server and avoid duplicating layout logic. (3) xhtml2pdf (mentioned in backend README) — current code uses ReportLab; we stay with ReportLab and fix list handling rather than switching stack.

---

## 3. Markdown export quality

**Decision**: **Keep export as passthrough of report content, with optional normalizer.** The backend `export_markdown` currently returns `content` unchanged. If the agent outputs correct Markdown (including numbered list for "Next troubleshooting steps"), the exported file is already well-formed. If we add a normalizer for that section (see §1), apply it before returning so the downloaded `.md` file also has numbered steps. No change to response type or API; still `text/markdown` with same endpoint.

**Rationale**: FR-004 requires well-formed Markdown that renders in common viewers. Passthrough plus prompt (and optional normalizer) is sufficient; no need for a full Markdown AST rewrite.

**Alternatives considered**: Running a Markdown prettifier or linter on export was rejected for MVP; we only need correct list syntax for one section.

---

## 4. In-browser report styling and accessibility

**Decision**: **Use the existing ReactMarkdown + Tailwind stack; add report-specific utility classes and semantic structure.** (1) **Hierarchy**: Keep or extend the existing `[&_h1]:...`, `[&_h2]:...`, `[&_h3]:...` so section headings are clearly distinct. (2) **Lists**: Ensure `<ol>` uses `list-decimal` and `<ul>` uses `list-disc` (already present in ReportView); add consistent spacing (`space-y-1` or similar) and indentation. (3) **Code**: Keep `pre`/`code` styling (monospace, background) and ensure sufficient contrast (DaisyUI theme). (4) **Long lines**: Add `break-words` or `overflow-wrap: break-word` on the report content container so long URLs/log lines wrap (FR-007). (5) **Accessibility (FR-008)**: ReactMarkdown emits semantic `<h1>`–`<h6>`, `<ol>`, `<ul>`, `<pre>`, `<code>`; ensure we do not strip or replace these with divs. Use theme colors that meet readable contrast; avoid fixed pixel font sizes for body text where possible (use rem/em or Tailwind scale) so zoom works. No new dependencies; no formal WCAG audit required.

**Rationale**: Spec requires clear hierarchy, readable typography, code distinction, and baseline a11y. Current component is close; we refine styles and add word-break. No need for a separate "prose" plugin if Tailwind utilities suffice; if the team later adds `@tailwindcss/typography`, it can be scoped to `.report-content` only.

**Alternatives considered**: A dedicated report CSS file was rejected for MVP in favor of Tailwind utilities and optional typography plugin. Client-side PDF generation for "same look as screen" was rejected (see §2).

---

## 5. Export failure handling (FR-009)

**Decision**: **Keep current behavior and harden message.** The frontend already catches export errors and shows a toast (`toast.error('Export failed', { description: msg })`). Ensure the description is user-friendly: prefer a short generic message (e.g. "Export failed. Try again.") when the backend returns 5xx or network error, and surface backend `detail` when it is a clear validation/404 message. No mandatory retry button in spec; implementation may add one.

**Rationale**: FR-009 requires a clear, user-friendly error message; the existing catch block satisfies this if the text is not technical. Backend already returns `detail` for PDF export failure (e.g. "PDF export failed. Please try again or use Markdown export."); frontend can use that as description when present.

**Alternatives considered**: Mandatory retry control was not required by spec; left to implementation.

---

## 6. Dependencies

**Decision**: **No new runtime dependencies for core behavior.** Frontend: continue using `react-markdown` (already in use in ReportView; add to `package.json` if currently missing). Backend: continue using `markdown` and `reportlab`; use stdlib `html.parser` for PDF list detection. Optional: `remark-gfm` on the frontend if we want GitHub-style tables in reports (spec does not require tables; can be added later).

**Rationale**: Minimize scope and dependency surface; stdlib and existing stack are sufficient to meet the spec.
