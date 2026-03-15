# Implementation Plan: App layout and navigation improvements

**Branch**: `006-layout-navbar-theme` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/006-layout-navbar-theme/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Improve app layout with four independently testable changes: (1) Add a theme switcher in the top bar (last item) using the theme-change library, with persistence and system-preference default. (2) Hide the left sessions sidebar on the knowledge page so only the top bar and main content are visible. (3) Remove the exact copy "Upload logs or switch session in the sidebar." and show one short instructional line when no session is selected. (4) Move "LogPilot" branding into the top bar on every page (not in the left sidebar); home page main content no longer uses "LogPilot" as the primary heading. Frontend-only; no new backend APIs or persistence beyond theme in localStorage via theme-change.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend unchanged)  
**Primary Dependencies**: React 18.x, React Router, Vite, Tailwind CSS, DaisyUI, theme-change, TanStack Query, Sonner, lucide-react  
**Storage**: Browser localStorage for theme preference (via theme-change; key `theme` or configurable). No server-side storage.  
**Testing**: Vitest + React Testing Library (frontend)  
**Target Platform**: Modern browsers (frontend dev server and production build)  
**Project Type**: Web application (frontend-only for this feature)  
**Performance Goals**: Instant theme apply; layout conditional on route (no extra network).  
**Constraints**: Theme switcher last in top bar; LogPilot only in top bar; sidebar hidden on `/knowledge`; accessibility (keyboard, aria, skip link).  
**Scale/Scope**: One theme control, one layout variant (sidebar visible vs hidden), copy and branding changes in existing components.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: No change; frontend continues to use existing backend (local or Docker). Theme is client-only (localStorage). ✓
- **Observability-First**: No change to logs/metrics/dashboards. ✓
- **Evidence-Backed AI**: No change to agent tools or output. ✓
- **User Stories**: Feature has four independently testable user stories (P1: theme switcher; P2: hide sidebar on knowledge page; P3: remove sidebar copy; P4: LogPilot in top bar) with acceptance criteria. ✓
- **Simplicity**: Scope is layout and one client preference (theme); no new services or APIs. ✓

*Post-Phase 1 re-check*: Design artifacts do not introduce new backend persistence or external APIs; constitution still satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/006-layout-navbar-theme/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (UI contract for top bar and layout)
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
│   ├── components/      # AppLayout (sidebar visibility by route, top bar: LogPilot + nav + theme switcher), HomePage (copy, no LogPilot heading)
│   ├── contexts/
│   ├── hooks/
│   ├── services/
│   ├── lib/
│   └── main.tsx         # themeChange(false) init for React
└── tests/
```

**Structure Decision**: Web application. This feature touches `frontend/src` only: AppLayout (conditional sidebar, top bar with LogPilot, nav links, theme switcher last), HomePage (remove old copy, add instructional line when no session, remove "LogPilot" as main heading), and app init for theme-change. Backend unchanged.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Table left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none)    | —          | —                                   |
