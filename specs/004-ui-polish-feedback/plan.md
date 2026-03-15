# Implementation Plan: UI polish — icons, copy, loading cues, and report-ready feedback

**Branch**: `004-ui-polish-feedback` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/004-ui-polish-feedback/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver UI polish across the LogPilot frontend: (1) clear visual loading indicators for all major async flows, (2) toast + subtle sound when a report becomes ready (including background), (3) consistent use of Lucid React icons where they add clarity, and (4) simplified, consistent platform copy. All changes are frontend-only; existing ReportGenerationContext is the integration point for report-ready notification.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend unchanged)  
**Primary Dependencies**: React 18.x, Vite, Tailwind CSS, DaisyUI, TanStack Query, Sonner (toasts); lucide-react (icons, to be added if not present)  
**Storage**: N/A (no new persistence)  
**Testing**: Vitest + React Testing Library (frontend)  
**Target Platform**: Modern browsers (frontend dev server and production build)  
**Project Type**: Web application (frontend-only changes for this feature)  
**Performance Goals**: Loading indicators visible within 2s; report-ready notification within polling cycle  
**Constraints**: Sound must be subtle and non-blocking; toast must work without sound for accessibility  
**Scale/Scope**: All main app surfaces (sessions, reports, log search, knowledge, upload, connection banner, modals)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: No change; frontend continues to talk to existing backend (local or Docker). ✓
- **Observability-First**: No change to logs/metrics/dashboards. ✓
- **Evidence-Backed AI**: No change to agent tools or output. ✓
- **User Stories**: Feature has four independently testable user stories (P1: loading cues, report-ready notification; P2: icons, copy) with acceptance criteria. ✓
- **Simplicity**: Scope is UI polish only; no new services, APIs, or data model. ✓

*Post-Phase 1 re-check*: Design artifacts (data-model, contracts, quickstart) do not introduce new persistence or external APIs; constitution still satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/004-ui-polish-feedback/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (report-ready notification)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── public/             # Static assets (e.g. report-ready.ogg for report-ready sound)
├── src/
│   ├── components/     # Loading UI, icons, copy changes
│   ├── contexts/       # ReportGenerationContext: trigger toast + sound on report ready
│   ├── hooks/
│   ├── services/
│   └── lib/            # reportReadyNotification helper, sound playback
└── tests/
```

**Structure Decision**: Web application layout. This feature touches only `frontend/src` (components, contexts, and optionally a small asset). Backend is unchanged.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Table left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| —         | —          | —                                   |
