# Implementation Plan: Report Visualization Improvement

**Branch**: `003-report-visualization-improvement` | **Date**: 2026-03-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-report-visualization-improvement/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Improve how incident reports are presented in the browser and in exported Markdown and PDF so that they are readable, professional, and consistent. The "Next troubleshooting steps" section MUST appear as a numbered list (1., 2., 3., …) everywhere; other sections may use bullet or numbered lists as appropriate. In-app report view gets clearer hierarchy, typography, spacing, and code styling; Markdown export remains well-formed; PDF export gains proper section hierarchy and numbered lists (currently all list items render as bullets). Baseline accessibility (semantic structure, contrast, zoom-friendly layout) and clear error messaging on export failure are required. Technical approach: (1) agent prompt update to require numbered list for "Next troubleshooting steps"; (2) frontend ReportView styling and optional content normalization for display; (3) backend export pipeline: Markdown passthrough with optional normalization, PDF generation updated to distinguish ordered vs unordered lists and improve layout; (4) export error handling already partially present (toast on catch)—ensure message is user-friendly per FR-009.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend); unchanged from 002  
**Primary Dependencies**: Frontend: React, ReactMarkdown (or equivalent), Tailwind CSS, DaisyUI; Backend: FastAPI, markdown, ReportLab (existing for PDF)  
**Storage**: N/A (report content from existing API; no new persistence)  
**Testing**: Vitest + React Testing Library (frontend); pytest (backend); manual validation for export output and a11y  
**Target Platform**: Modern browsers (in-app view); exported Markdown/PDF consumed in standard viewers/readers  
**Project Type**: Web application (frontend + backend); this feature touches frontend report UI and backend export only  
**Performance Goals**: Report render and export feel responsive; no strict latency target; PDF generation for typical report length (&lt;50 KB content) acceptable  
**Constraints**: Baseline accessibility (semantic headings/lists, contrast, zoom); long lines must wrap; export failure must show clear error message (FR-009)  
**Scale/Scope**: Single report view/export per user; same scale as existing report flow

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: Design supports local deployment; no mandatory cloud egress. **PASS** — no change to deployment; report view and export run on existing frontend/backend.
- **Observability-First**: Logs, metrics, dashboards unchanged. **PASS** — feature is presentation only.
- **Evidence-Backed AI**: Agent uses only approved tools; structured output; no production remediation. **PASS** — we only tighten report format (numbered troubleshooting steps) in the agent prompt; no new tools or execution.
- **User Stories**: Feature is specified as independently testable user stories with acceptance criteria. **PASS** — spec has 4 user stories (P1–P2) with acceptance scenarios.
- **Simplicity**: Scope within PRD; extra complexity documented. **PASS** — scope is presentation and formatting only; out-of-scope list in spec; no new services.

**Post Phase 1**: Data model and contracts do not introduce new constitution violations. Changes are confined to frontend report component, backend export service, and agent prompt.

## Project Structure

### Documentation (this feature)

```text
specs/003-report-visualization-improvement/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (report content format)
└── tasks.md             # Phase 2 output (/speckit.tasks — not created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/reports.py    # Export endpoint (unchanged signature; behavior per FR-009)
│   └── services/
│       ├── agent.py      # Prompt update: "Next troubleshooting steps" as numbered list
│       └── export.py     # export_markdown (optional normalizer), export_pdf (ol/ul, layout)
└── tests/

frontend/
├── src/
│   ├── components/
│   │   └── ReportView.tsx   # Styling, hierarchy, code blocks, long-line wrap, a11y
│   └── services/api.ts      # Export error handling (user-facing message)
└── tests/
```

**Structure Decision**: Existing backend and frontend layout from 002; no new top-level modules. All work is in `backend/app/services/agent.py`, `backend/app/services/export.py`, `frontend/src/components/ReportView.tsx`, and optional shared/normalizer if we add content normalization.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|-------------|--------------------------------------|
| *(none)* | — | — |
