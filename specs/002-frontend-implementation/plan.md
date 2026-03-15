# Implementation Plan: Log Investigation Frontend

**Branch**: `002-frontend-implementation` | **Date**: 2026-03-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-frontend-implementation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement a web frontend for the LogPilot log investigation platform so engineers can manage sessions, upload log archives, search and inspect logs, access session-scoped metrics/dashboards via link, run knowledge ingest/search, and trigger report generation with viewing and export (Markdown/PDF). The frontend is a single-page application that consumes the existing FastAPI backend; technology choice is **Vite + React + Tailwind CSS + DaisyUI + TanStack Query + Zod + React Hook Form + date-fns + Sonner** (see research.md). Sonner toasts are styled with DaisyUI’s alert classes for a consistent look. All flows are API-driven and session-scoped; metrics/dashboards are opened in a new tab (e.g. Grafana) with session context.

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), React 18.x; backend remains Python 3.11+  
**Primary Dependencies**: Vite, React, React Router, Tailwind CSS, DaisyUI, TanStack Query (@tanstack/react-query), Zod, React Hook Form (+ @hookform/resolvers), date-fns, Sonner; backend: FastAPI (existing)  
**Storage**: None on frontend; session/report state from backend API; optional local state (e.g. current session id in memory or localStorage for UX)  
**Testing**: Vitest (unit), React Testing Library; optional Playwright/Cypress for E2E  
**Target Platform**: Modern browsers (ES2020+); served as static assets; dev proxy to backend  
**Project Type**: web-application (SPA frontend + existing backend)  
**Performance Goals**: Fast initial load and HMR in development; interactive flows (upload, search, report poll) feel responsive; no hard target for req/s  
**Constraints**: Backend base URL configurable (env); CORS already allowed by backend; basic a11y (keyboard, focus order, labels)  
**Scale/Scope**: Single-user/local-first; ~6 main user stories; ~10–15 main screens/views

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: Design supports local deployment (e.g., Docker Compose); no mandatory cloud egress. **PASS** — frontend is static SPA; backend and stack run locally; no third-party data egress required.
- **Observability-First**: Logs → queryable store; metrics derived and exposed; dashboards provisioned. **PASS** — frontend exposes log search and links to Grafana; backend/Loki/Prometheus/Grafana unchanged.
- **Evidence-Backed AI**: Agent uses only approved tools; structured output; no production remediation. **PASS** — frontend only triggers report generation and displays results; no change to agent behavior.
- **User Stories**: Feature is specified as independently testable user stories with acceptance criteria. **PASS** — spec has 6 user stories (P1–P6) with acceptance scenarios and priorities.
- **Simplicity**: Scope within PRD; extra complexity documented in Complexity Tracking table below. **PASS** — scope is “implement the frontend” per spec; no additional scope.

**Post Phase 1**: Data model, contracts, and quickstart do not introduce new constitution violations. Frontend remains a consumer of existing backend and local stack.

## Project Structure

### Documentation (this feature)

```text
specs/002-frontend-implementation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/             # Existing: sessions, upload, logs, reports, knowledge
│   ├── lib/
│   └── services/
└── tests/

frontend/
├── src/
│   ├── components/      # Reusable UI (session list, upload, log table, report view, etc.)
│   ├── pages/           # Route-level views (sessions, upload, search, knowledge, reports)
│   ├── services/        # API client (fetch to backend base URL)
│   ├── hooks/           # Optional: useSessions, useReportPoll, etc.
│   ├── App.tsx          # Root component (routing, layout)
│   └── main.tsx         # Entry point (QueryClientProvider, React root)
├── public/
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── package.json
└── tests/
```

**Structure Decision**: Existing `backend/` is unchanged. New `frontend/` is a Vite + React SPA; structure follows Option 2 (Web application) with `frontend/src` containing components, pages, and API services. Contracts document the backend API consumed by the frontend.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. Table left empty.
