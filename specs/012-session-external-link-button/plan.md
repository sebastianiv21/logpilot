# Implementation Plan: Session External Link Button in Main Content

**Branch**: `012-session-external-link-button` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/012-session-external-link-button/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a control in the main content area, to the right of the session title, that opens the session’s external link (the URL provided in the session create/edit form) in a new tab when present. The control is always shown (icon + "External link" text). When the session has a non-empty external link, it is enabled (anchor with `target="_blank"` and `rel="noopener noreferrer"`). When the session has no external link (missing, null, or empty/whitespace-only), the control is disabled and shows a tooltip (e.g. "No external link provided"). It is keyboard-focusable with an appropriate accessible name when enabled or disabled. Implementation is frontend-only: extend the title block in `App.tsx` to always render the control—enabled (anchor) or disabled (with tooltip)—using `currentSession.external_link` and lucide-react for the icon.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend); Python 3.11+ (backend unchanged)  
**Primary Dependencies**: React 18.x, React Router, Vite, Tailwind CSS, DaisyUI, TanStack Query, Sonner, lucide-react  
**Storage**: N/A (session and `external_link` from existing API; no new persistence)  
**Testing**: Vitest / React Testing Library for frontend (existing); no new backend tests  
**Target Platform**: Browser (modern); local or deployed frontend  
**Project Type**: Web application (frontend + backend; this feature is frontend-only)  
**Performance Goals**: No new network calls; control render is conditional on existing session data  
**Constraints**: External link opens in new tab; control always visible—enabled when session has non-empty `external_link`, disabled with tooltip otherwise; accessibility (keyboard + screen reader) required  
**Scale/Scope**: Single-user app; one control per main content view; typical session count low

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: Design supports local deployment; no new cloud or egress; control only navigates to user-provided URL. **PASS**
- **Observability-First**: No change to logs/metrics/dashboards; feature is UX only. **PASS**
- **Evidence-Backed AI**: No change to agent tools or output. **PASS**
- **User Stories**: Spec has P1 (open session external link from main content) with acceptance criteria. **PASS**
- **Simplicity**: Single UI control; no new routes or APIs; uses existing Session and `external_link`. **PASS**

## Project Structure

### Documentation (this feature)

```text
specs/012-session-external-link-button/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1 (UI contract for main-content external link)
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── App.tsx           # HomePage: title block; add external-link control next to session title
│   ├── components/      # (optional) extract title + control into a small component
│   └── ...
└── ...
```

**Structure Decision**: Web app with frontend-only changes. No new backend or routes. The control is added in the same place the session title is rendered (currently `App.tsx` HomePage); optional refactor to a small presentational component for the "title row" (title + optional external link + session ID) is an implementation choice.

## Phase 0: Research

See [research.md](./research.md). Resolved: external-link control pattern (anchor with `target="_blank"` and `rel="noopener noreferrer"`), icon + text + aria-label for accessibility.

## Phase 1: Design & Contracts

- **Data model**: No new entities. Session already has optional `external_link`; see [data-model.md](./data-model.md).
- **Contracts**: UI contract for the main-content external link control in [contracts/main-content-external-link.md](./contracts/main-content-external-link.md).
- **Quickstart**: [quickstart.md](./quickstart.md) for manual verification.

## Constitution Check (post–Phase 1 design)

Re-verified after data-model, contracts, and quickstart:

- **Local-First**: No new backend or egress; control only opens user-provided URL in new tab. **PASS**
- **Observability-First**: No change to logs/metrics/dashboards. **PASS**
- **Evidence-Backed AI**: No change to agent. **PASS**
- **User Stories**: P1 and acceptance scenarios reflected in contract and quickstart. **PASS**
- **Simplicity**: One control, conditional on existing `Session.external_link`; no new state or routes. **PASS**

## Complexity Tracking

> No constitution violations. Table left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none)    | —          | —                                   |
