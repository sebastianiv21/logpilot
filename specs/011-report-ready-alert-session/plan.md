# Implementation Plan: Report-Ready Alert Shows Session Context and Go-to-Session Action

**Branch**: `011-report-ready-alert-session` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/011-report-ready-alert-session/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Extend the existing report-ready notification (toast + sound) so that: (1) every toast message includes the session identity (name or session ID, with fallback when name cannot be loaded); (2) a "View report" action button in the toast navigates the user to the session and opens that report. The control must be keyboard-focusable and have an accessible name. Implementation is frontend-only: update `reportReadyNotification.ts` to always include session label and add a Sonner toast action; introduce a small context or callback to "open report" (set current session + open report modal); update the report-ready contract and ReportList to honor open-report intent.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend unchanged)  
**Primary Dependencies**: React 18.x, React Router, Vite, Tailwind CSS, DaisyUI, TanStack Query, Sonner (toast), lucide-react  
**Storage**: N/A (session/report from existing API; optional localStorage for current session already exists)  
**Testing**: Vitest / React Testing Library for frontend (existing); no new backend tests  
**Target Platform**: Browser (modern); local or deployed frontend  
**Project Type**: Web application (frontend + backend; this feature is frontend-only)  
**Performance Goals**: Toast and action respond immediately; no new network round-trip for notification itself  
**Constraints**: Toast duration/position/sound unchanged (out of scope); accessibility (keyboard + screen reader) required for "View report"  
**Scale/Scope**: Single-user app; one report-ready toast per report; typical sessions/reports count low

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: Design supports local deployment; no new cloud or egress; notification and navigation are in-browser only. **PASS**
- **Observability-First**: No change to logs/metrics/dashboards; feature is UX only. **PASS**
- **Evidence-Backed AI**: No change to agent tools or output. **PASS**
- **User Stories**: Spec has P1 (session identity in alert) and P2 (View report → session + report) with acceptance criteria. **PASS**
- **Simplicity**: Scope limited to alert content + one control; no new routes required if open-report is handled via context. **PASS**

## Project Structure

### Documentation (this feature)

```text
specs/011-report-ready-alert-session/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/          # Phase 1 (report-ready-notification update)
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/      # ReportList.tsx (consume open-report intent)
│   ├── contexts/        # SessionContext.tsx (existing); optional ReportToOpenContext or extend SessionContext
│   ├── lib/             # reportReadyNotification.ts (message + action; pass reportId)
│   └── ...
└── ...
```

**Structure Decision**: Web app with frontend-only changes. No new backend or routes; optional lightweight context for "report to open" so ReportList can open the modal when session matches.

## Constitution Check (post–Phase 1 design)

Re-verified after data-model, contracts, and quickstart:

- **Local-First**: No new backend or egress; report-to-open and toast action are in-browser. **PASS**
- **Observability-First**: No change to logs/metrics/dashboards. **PASS**
- **Evidence-Backed AI**: No change to agent. **PASS**
- **User Stories**: P1/P2 and acceptance scenarios reflected in contract and quickstart. **PASS**
- **Simplicity**: Context-based “report to open” and Sonner action; no new routes. **PASS**

## Complexity Tracking

> No constitution violations. Table left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none)    | —          | —                                   |
