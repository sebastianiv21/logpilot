# Implementation Plan: Upload State Scoped Per Session and Persistent Across Refresh

**Branch**: `010-upload-session-state-fix` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/010-upload-session-state-fix/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Fix two issues: (1) When the user switches sessions, the upload summary must show only the current session’s result (or empty)—no cross-session display. (2) After a full page refresh, the app must still know which sessions have logs and show the last upload summary for the selected session (loading state, error + retry for selected session only, success feedback after retry). Technical approach: scope upload result UI by current session id; persist “has logs” and last upload result on the backend so the frontend can refetch on load; add loading and error+retry UX per spec clarifications.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11+ (backend)  
**Primary Dependencies**: React 18.x, TanStack Query, FastAPI; existing SessionContext, UploadLogs, upload API  
**Storage**: Backend: SQLite (existing sessions + session_log_extent); add storage for last upload result per session (new table or columns). Frontend: no new persistence; continue storing currentSessionId in localStorage.  
**Testing**: Vitest + React Testing Library (frontend); pytest (backend, for new/updated endpoints and repository)  
**Target Platform**: Modern browsers; same as existing app  
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: Loading state visible until refetch completes; session switch and refresh show loading then correct state (no quantified latency target in spec)  
**Constraints**: Retry scoped to selected session only; no full reload of all session states on retry  
**Scale/Scope**: All sessions in the list; one current session; last upload result per session (single summary, not full history)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: No change; backend remains locally deployable; new state is stored server-side under user control. ✓
- **Observability-First**: No change to logs/metrics/dashboards; feature restores correct display of upload summary and “has logs” state. ✓
- **Evidence-Backed AI**: No change to agent tools or output. ✓
- **User Stories**: Feature has two independently testable user stories (P1: session-scoped upload result; P2: state survives refresh with loading/retry/success feedback) with acceptance criteria. ✓
- **Simplicity**: Scope is bounded to session-scoped UI state and persistence/refetch of “has logs” + last upload summary; complexity documented in research (backend vs frontend persistence). ✓

*Post-Phase 1 re-check*: Design adds minimal backend storage and one new (or extended) endpoint; frontend adds refetch, loading, and retry flows. Constitution still satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/010-upload-session-state-fix/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contract for upload summary / has_logs)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/             # New or extended: GET upload summary and/or has_logs in session response
│   ├── lib/             # DB schema + SessionRepository: store/read last upload result
│   └── services/        # upload.py: persist result after pipeline
└── tests/

frontend/
├── src/
│   ├── components/      # UploadLogs: scope result by currentSessionId; loading/error/retry UI
│   ├── contexts/       # SessionContext: hydrate sessionIdsWithLogs (and optional last result) from API on load
│   ├── hooks/           # Optional: useSessionUploadState(sessionId) for fetch + loading + retry
│   └── services/        # api.ts: getUploadSummary(sessionId), getSessionHasLogs (or from session list)
└── tests/
```

**Structure Decision**: Web application. Backend gains persistent storage for last upload result per session and an endpoint (or extended session response) to expose it and “has logs”. Frontend: scope UploadLogs display by current session; on app load (and on session change) fetch “has logs” and last upload summary for the selected session; show loading indicator, on failure show error + retry (selected session only), on success show state + brief success message; clear or overwrite displayed result when session changes so only the current session’s result is shown.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Table left empty.
