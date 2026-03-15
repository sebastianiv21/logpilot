# Implementation Plan: Knowledge base config route and layout improvements

**Branch**: `005-kb-config-route-layout` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/005-kb-config-route-layout/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Move the knowledge base (ingestion and search) off the main screen onto a dedicated route (`/knowledge`), reachable from an upper-right control in the main-content navbar: database icon + status indicator (red / yellow / green, tooltip "Knowledge base"). Add an in-app return control on the KB page and improve main-screen layout hierarchy without reordering sections. Frontend-only; existing GET /knowledge/ingest/status drives the indicator state.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend unchanged)  
**Primary Dependencies**: React 18.x, React Router, Vite, Tailwind CSS, DaisyUI, TanStack Query, Sonner; lucide-react (Database icon)  
**Storage**: N/A (no new persistence; KB status from existing API)  
**Testing**: Vitest + React Testing Library (frontend)  
**Target Platform**: Modern browsers (frontend dev server and production build)  
**Project Type**: Web application (frontend-only for this feature)  
**Performance Goals**: Route navigation and status indicator update within existing polling (e.g. 2s when running)  
**Constraints**: Single click to config route; icon + indicator only with tooltip; accessibility (keyboard, aria-label, status announced)  
**Scale/Scope**: One new route, one new header control, main and KB page layout tweaks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: No change; frontend continues to use existing backend (local or Docker). ✓
- **Observability-First**: No change to logs/metrics/dashboards. ✓
- **Evidence-Backed AI**: No change to agent tools or output. ✓
- **User Stories**: Feature has three independently testable user stories (P1: upper-right control + KB route; P2: route + return; P3: layout hierarchy) with acceptance criteria. ✓
- **Simplicity**: Scope is one new route, one header control, layout polish; no new services or APIs. ✓

*Post-Phase 1 re-check*: Design artifacts do not introduce new persistence or external APIs; constitution still satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/005-kb-config-route-layout/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (UI contract for header + route)
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
├── src/
│   ├── components/      # AppLayout (header + KB link), KnowledgePage, KnowledgeIngest, KnowledgeSearch; optional HeaderKbLink
│   ├── contexts/
│   ├── hooks/           # useKnowledgeIngest (existing; status for indicator)
│   ├── services/
│   └── lib/
└── tests/
```

**Structure Decision**: Web application. This feature touches `frontend/src`: new route and page component, AppLayout extended with a main-content navbar (top bar with upper-right KB link + indicator, and optionally a Home/back link when on the knowledge page), HomePage without KB section; optional layout tweaks for hierarchy. Backend unchanged.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Table left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| —         | —          | —                                   |
