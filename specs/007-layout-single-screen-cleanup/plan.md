# Implementation Plan: Single-Screen Layout, Pagination, and Copy Cleanup

**Branch**: `007-layout-single-screen-cleanup` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/007-layout-single-screen-cleanup/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a single-screen session view, paginated sessions and KB search (Load more + optional Previous), Back to Home inside the knowledge space content, top-bar home link and app icon, deduplicated copy/icons, and visual upload/processing summary via a charts library. Layout uses right-side space (horizontal/multi-column); no collapsible sections—scroll if needed. Frontend-focused; backend may gain optional pagination params for sessions/KB search (see research and contracts). Batch size fixed at 10 (no user control); same pagination pattern for both lists.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend unchanged)  
**Primary Dependencies**: React 18.x, React Router, Vite, Tailwind CSS, DaisyUI, TanStack Query, Sonner, lucide-react; add a charts library (see research.md)  
**Storage**: No new server storage; optional localStorage for batch-size preference (implementation choice)  
**Testing**: Vitest + React Testing Library (frontend); pytest (backend, if API changes)  
**Target Platform**: Modern browsers; typical desktop viewport ≥1280×720 for single-screen target  
**Project Type**: Web application (frontend + backend; this feature is mostly frontend)  
**Performance Goals**: Single-screen fit at target viewport; paginated lists avoid unbounded DOM; charts render without blocking  
**Constraints**: Rearrange-only layout (no collapsible sections); scroll acceptable when content doesn’t fit; Back to Home in KB content only; same pagination pattern for sessions and KB search  
**Scale/Scope**: Sessions list and KB search paginated (batch 10/20/50); upload summary visualized; layout and copy/icon cleanup across session and KB views

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: No change; frontend uses existing backend (local or Docker). No mandatory cloud. ✓
- **Observability-First**: No change to logs/metrics/dashboards; upload summary visualization improves scanability of processing results. ✓
- **Evidence-Backed AI**: No change to agent tools or output. ✓
- **User Stories**: Feature has five independently testable user stories (P1: single-screen + layout + sessions pagination + upload charts; P2: KB search pagination + batch size; P3: Back to Home in KB content; P4: copy/icon dedup; P5: top-bar home link and icon) with acceptance criteria. ✓
- **Simplicity**: Scope is layout, pagination, navigation, copy/icons, and one charts dependency; complexity documented in research (charts choice) and data-model. ✓

*Post-Phase 1 re-check*: Design artifacts do not introduce new backend persistence beyond optional pagination params; constitution still satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/007-layout-single-screen-cleanup/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (UI / API contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   ├── services/
│   └── api/             # Optional: pagination params for GET /sessions, KB search (see contracts)
└── tests/

frontend/
├── src/
│   ├── components/      # SessionList (paginated), KnowledgeSearch (paginated), UploadLogs (charts),
│   │                    # AppLayout (top bar: clickable LogPilot + app icon), KnowledgePage (Back to Home in content)
│   ├── contexts/
│   ├── hooks/           # useSessionsList (paginated), useKnowledgeSearch (paginated), batch size state
│   ├── services/
│   ├── lib/
│   └── main.tsx
└── tests/
```

**Structure Decision**: Web application. This feature touches `frontend/src` primarily: layout (grid/columns to use right-side space), SessionList and KnowledgeSearch with Load more + optional Previous and batch-size control, UploadLogs with charts for processing summary, AppLayout for clickable LogPilot + Lucide app icon, KnowledgePage for in-content Back to Home and copy/icon cleanup. Backend may add optional query params for sessions and KB search (limit/offset or limit/cursor) to support pagination; see contracts.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Table left empty.
