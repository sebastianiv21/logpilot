# Implementation Plan: Scrollable Session List and Dynamic Session Titles with Copy ID

**Branch**: `008-scrollable-session-list-titles` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/008-scrollable-session-list-titles/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Deliver a self-contained scrollable session list in the sidebar (only the list scrolls, not the whole page), dynamic section titles for Logs & metrics and Reports (current session name or "Session" + first 8 chars of ID), a session ID line with copy control under each section title (full ID + accessible copy button with success/failure feedback), and handling for no session / long name / clipboard failure. Frontend-only; no backend changes. Reuses existing Session type and session list/sidebar ID prefix (8 chars); adds scroll container, section header component, and clipboard + toast feedback.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend); Python 3.11+ (backend unchanged)  
**Primary Dependencies**: React 18.x, React Router, Vite, Tailwind CSS, DaisyUI, TanStack Query, Sonner (toasts), lucide-react  
**Storage**: No new persistence; current session from SessionContext + sessions from existing API  
**Testing**: Vitest + React Testing Library (frontend)  
**Target Platform**: Modern browsers; desktop viewport  
**Project Type**: Web application (frontend-only feature)  
**Performance Goals**: No full-page scroll when scrolling session list; instant title/ID update on session change  
**Constraints**: Session list scroll region must not scroll main content; copy feedback via same channel (toast); accessible name on copy control  
**Scale/Scope**: One scrollable sidebar region; two section headers (Logs & metrics, Reports) with shared pattern; clipboard and truncation/tooltip in UI only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: No change; frontend uses existing backend. No mandatory cloud. ✓
- **Observability-First**: No change to logs/metrics/dashboards. ✓
- **Evidence-Backed AI**: No change to agent tools or output. ✓
- **User Stories**: Feature has three independently testable user stories (P1: scrollable session list; P2: dynamic section titles; P3: full session ID + copy) with acceptance criteria. ✓
- **Simplicity**: Scope is layout (scroll container), section headers (title + ID + copy), and clipboard/feedback; no new backend or storage. ✓

*Post-Phase 1 re-check*: Design artifacts do not introduce new persistence or external services; constitution still satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/008-scrollable-session-list-titles/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (UI contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/                  # No changes for this feature
frontend/
├── src/
│   ├── components/      # SessionList (wrap in scroll container), AppLayout (sidebar layout),
│   │                    # HomePage / section headers: SessionSectionHeader or inline title + SessionIdCopy
│   ├── contexts/        # SessionContext (unchanged)
│   ├── hooks/           # useSessionsList, useCurrentSession (unchanged); optional useCopySessionId
│   └── lib/             # schemas (Session unchanged)
└── tests/
```

**Structure Decision**: Web application. This feature touches `frontend/src/components` (AppLayout sidebar scroll region, SessionList wrapper, section titles and session ID + copy in HomePage or a shared header component). Copy behavior is implemented inline in App.tsx; an optional useCopySessionId hook is deferred. No new routes or backend endpoints.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Table left empty.
