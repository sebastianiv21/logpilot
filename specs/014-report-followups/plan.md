# Implementation Plan: Report Follow-Up Improvements

**Branch**: `014-report-followups` | **Date**: 2026-03-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-report-followups/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add four report follow-ups across the existing report flow: store and surface the incident question in report history, add a dedicated "Coding agent fix prompt" section to generated reports, add a compact copy button in the rendered report viewport that copies Markdown, and harden PDF export so it reliably produces a readable document or a clear failure. Technical approach: extend the report persistence/API shape with question metadata, update the agent report contract and prompt to emit the new section, reuse report Markdown as the single source for viewport copy and export, and strengthen the backend PDF export path plus tests around representative report content.

## Technical Context

**Language/Version**: TypeScript 5.9 + React 19 (frontend), Python 3.14 (backend)  
**Primary Dependencies**: Frontend: Vite, React Router, TanStack Query, React Hook Form, Zod, ReactMarkdown, DaisyUI, Tailwind, Sonner, Lucide React; Backend: FastAPI, Pydantic, markdown, ReportLab, sqlite3  
**Storage**: SQLite metadata store for sessions and reports; existing `reports` table requires additive schema evolution for question persistence  
**Testing**: Vitest + React Testing Library + jsdom (frontend); pytest (backend); targeted manual validation for clipboard and PDF output  
**Target Platform**: Local-first web app in modern desktop browsers, with backend running locally or in Docker Compose  
**Project Type**: Web application with split frontend/backend and local infrastructure services  
**Performance Goals**: Report detail view remains responsive during polling and copy actions; PDF export succeeds for typical report sizes without hangs or excessive latency; report history remains scannable with many entries  
**Constraints**: No new mandatory cloud services; preserve evidence-backed structured report flow; keep report history lightweight; copy action must use Markdown; PDF failures must surface clear user feedback  
**Scale/Scope**: Existing single-user MVP session/report workflow; multiple historical reports per session; one report generation request at a time per session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: **PASS** — changes stay within the existing local frontend/backend/SQLite workflow and do not introduce new external services.
- **Observability-First**: **PASS** — the feature builds on report generation/export UX and does not weaken logs/metrics/dashboard flows.
- **Evidence-Backed AI**: **PASS** — agent still uses only approved tools; the report contract is extended with a new user-visible section but remains structured and read-only.
- **User Stories**: **PASS** — spec contains independently testable stories for report content, history context, copy behavior, and PDF export.
- **Simplicity**: **PASS** — additive changes in existing report modules, repository schema, and API responses; no new subsystem or service boundary required.

**Post Phase 1 Check**: PASS — design remains within the existing frontend/backend split, uses additive schema changes only, and keeps report generation/export as the single report-content pipeline.

## Project Structure

### Documentation (this feature)

```text
specs/014-report-followups/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── report-history-and-export.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── reports.py
│   ├── lib/
│   │   ├── db.py
│   │   └── repositories.py
│   ├── models/
│   │   └── report.py
│   └── services/
│       ├── agent.py
│       └── export.py
└── tests/
    ├── contract/
    └── unit/

frontend/
├── src/
│   ├── components/
│   │   ├── ReportGenerate.tsx
│   │   ├── ReportList.tsx
│   │   └── ReportView.tsx
│   ├── hooks/
│   │   └── useReports.ts
│   ├── lib/
│   │   └── schemas.ts
│   └── services/
│       └── api.ts
└── tests/
```

**Structure Decision**: Keep the current split web-app structure. Backend owns report persistence, generation prompt, and export behavior; frontend owns list/detail rendering, copy interaction, and history preview UX. Tests should be added alongside the existing backend/frontend test suites rather than introducing a new package.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | — | — |
