# Implementation Plan: Session Search Bar

**Branch**: `009-session-search-bar` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/009-session-search-bar/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a session search bar directly above the scrollable session list in the sidebar. Users filter sessions by typing text; matching is case-insensitive substring against session name, session ID, and external link. Input is trimmed (whitespace-only treated as empty → show full list). The filtered list updates after a short debounce (150–300 ms) after typing stops. Empty state shows a clear “no sessions match” message. Accessible label and live region announce result count or “no sessions match”. Frontend-only; no backend or API changes. Reuses existing Session type and session list API; adds search input, filter state, debounce, and a11y (label + live region).

## Technical Context

**Language/Version**: TypeScript 5.x (frontend); Python 3.11+ (backend unchanged)  
**Primary Dependencies**: React 18.x, React Router, Vite, Tailwind CSS, DaisyUI, TanStack Query, Sonner, lucide-react  
**Storage**: No new persistence; filter query is ephemeral UI state (search input value)  
**Testing**: Vitest + React Testing Library (frontend)  
**Target Platform**: Modern browsers; desktop viewport  
**Project Type**: Web application (frontend-only feature)  
**Performance Goals**: Filter applied after 150–300 ms debounce; no jank while typing  
**Constraints**: Substring match, case-insensitive; trim whitespace; accessible label + live region for results  
**Scale/Scope**: One search input above session list; client-side filter over existing sessions array

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: No change; frontend uses existing backend. No mandatory cloud. ✓
- **Observability-First**: No change to logs/metrics/dashboards. ✓
- **Evidence-Backed AI**: No change to agent tools or output. ✓
- **User Stories**: Feature has two independently testable user stories (P1: search by name/ID/link; P2: empty state) with acceptance criteria. ✓
- **Simplicity**: Scope is one search input, client-side filter, debounce, and a11y; no new backend or storage. ✓

*Post-Phase 1 re-check*: Design artifacts do not introduce new persistence or external services; constitution still satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/009-session-search-bar/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (UI contract for search bar)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/                  # No changes for this feature
frontend/
├── src/
│   ├── components/      # SessionList (add filter + empty state), AppLayout (search bar above list)
│   │                    # New: session search input + optional wrapper; live region for result count
│   ├── contexts/        # SessionContext (unchanged)
│   ├── hooks/           # useSessionsList (unchanged); optional useDebouncedValue for search
│   └── lib/             # schemas (Session unchanged)
└── tests/
```

**Structure Decision**: Web application. This feature touches `frontend/src/components`: add a search input directly above the scrollable session list in the sidebar (AppLayout), and filter the sessions inside SessionList (or a thin wrapper) by trimmed, case-insensitive substring on name, id, external_link. Debounce the search input (150–300 ms). Add accessible label and live region for result count / "no sessions match". No new routes or backend endpoints.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Table left empty.
