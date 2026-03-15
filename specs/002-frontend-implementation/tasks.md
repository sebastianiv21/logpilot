# Tasks: Log Investigation Frontend

**Input**: Design documents from `/specs/002-frontend-implementation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US6)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`, `frontend/tests/` (per plan.md). Run dev server: `cd frontend && npm run dev`
- **Backend**: Existing `backend/`; API base URL via `VITE_API_BASE` (e.g. http://localhost:8000)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Frontend project initialization and basic structure

- [X] T001 Create frontend directory structure per plan.md: frontend/src/components, frontend/src/pages, frontend/src/services, frontend/src/hooks, frontend/src/App.tsx, frontend/public, frontend/index.html, frontend/vite.config.ts, frontend/tailwind.config.js, frontend/package.json, frontend/tests
- [X] T002 Initialize Vite + React + TypeScript project in frontend/ with dependencies: react, react-dom, react-router-dom, tailwindcss, daisyui, @tanstack/react-query, zod, react-hook-form, @hookform/resolvers, date-fns, sonner (see research.md)
- [X] T003 [P] Configure Tailwind CSS and DaisyUI in frontend/tailwind.config.js
- [X] T004 [P] Add frontend env: VITE_API_BASE and VITE_GRAFANA_URL in frontend/.env.example; configure Vite proxy to backend in frontend/vite.config.ts if desired
- [X] T005 [P] Configure Vitest and React Testing Library in frontend/ (package.json + config)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create API client module: base URL from import.meta.env.VITE_API_BASE, fetch wrapper for JSON requests and error handling (detail from backend) in frontend/src/services/api.ts
- [X] T007 [P] Add Zod schemas for API response types (Session, SessionList, UploadResult, LogsQuery, Report, ReportList, KnowledgeIngestStatus, KnowledgeSearch) per data-model.md and contracts/api.md in frontend/src/lib/schemas.ts
- [X] T008 Setup QueryClientProvider and React Query default options in frontend/src/main.tsx (Vite entry point; root component remains App.tsx)
- [X] T009 Setup React Router with root layout and routes (e.g. /, /session/:sessionId or single layout with session scope) in frontend/src/App.tsx
- [X] T010 Add current session state and persistence (e.g. React context + localStorage for session id) so all session-scoped features use it. Implement in either frontend/src/contexts/SessionContext.tsx or frontend/src/hooks/useCurrentSession.ts; either approach is acceptable.
- [X] T011 Add Sonner Toaster with DaisyUI alert styling (unstyled + toastOptions.classNames.toast mapping success/error/info to alert alert-success/alert-error/alert-info) in frontend/src/App.tsx per research.md §8
- [X] T012 Add app shell/layout: nav or sidebar for session list, current session indicator, and area for session-scoped content in frontend/src/components/AppLayout.tsx (or equivalent layout component)

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — Session Management (Priority: P1) — MVP

**Goal**: Create and switch between sessions; optional name and external link; list shows creation time and details; select and edit session. When no sessions exist, allow creating the first session and set it as current so upload and other actions are possible.

**Independent Test**: Create multiple sessions with names/links, list them, select one as current, edit name/link; confirm list and detail show updated data. With zero sessions, create first session and confirm it becomes current.

- [X] T013 [US1] Implement sessions API: GET /sessions, POST /sessions, GET /sessions/{id}, PATCH /sessions/{id} in frontend/src/services/api.ts and TanStack Query hooks (useQuery for list/get, useMutation for create/update) in frontend/src/hooks/useSessions.ts
- [X] T014 [US1] Build SessionList component: list all sessions with creation time (date-fns), name, external link, and clear current/selected indicator in frontend/src/components/SessionList.tsx
- [X] T015 [US1] Build CreateSession form (optional name, optional external link) with React Hook Form and Zod validation in frontend/src/components/CreateSessionForm.tsx
- [X] T016 [US1] Build session selection (set current session in context) and edit session (inline or modal: name, external link) with PATCH mutation and cache invalidation in frontend/src/components/SessionList.tsx or frontend/src/components/EditSessionForm.tsx
- [X] T017 [US1] Integrate SessionList, CreateSession, and current session into app layout; ensure one session is selectable as current and UI indicates active session in frontend/src/pages/ or frontend/src/App.tsx

**Checkpoint**: User Story 1 complete — session management works independently

---

## Phase 4: User Story 2 — Log Upload and Upload Results (Priority: P2)

**Goal**: Upload a compressed log archive for the current session; show progress/loading and then success or failure with summary (files processed, lines parsed/rejected, files skipped); clear errors for size limit or invalid archive.

**Independent Test**: Select a session, upload a valid .zip, verify success and summary; upload invalid or oversized file and verify error message.

- [ ] T018 [US2] Implement upload API: POST /sessions/{session_id}/logs/upload (multipart/form-data, field "file") and parse UploadResultResponse in frontend/src/services/api.ts
- [ ] T019 [US2] Build UploadLogs component: file input (accept .zip), loading state during upload, display result (status, files_processed, files_skipped, lines_parsed, lines_rejected) or error message in frontend/src/components/UploadLogs.tsx
- [ ] T020 [US2] Map backend errors (404, 413, 400) to user-friendly messages and show via Sonner toast or inline; do not indicate success on failure (FR-004, FR-011) in frontend/src/components/UploadLogs.tsx

**Checkpoint**: User Story 2 complete — upload and result display work

---

## Phase 5: User Story 3 — Log Search and Inspection (Priority: P3)

**Goal**: Search and filter logs for the current session by time range and labels (service, environment, log level); view matching log lines with raw message and metadata; default time range = full extent of session logs; pagination or limit with “load more” or count.

**Independent Test**: With a session that has ingested logs, set filters and time range, run search, verify log lines and metadata; empty result shows “no logs match”.

- [ ] T021 [US3] Implement logs query API: POST /sessions/{session_id}/logs/query with body (start, end, limit, service, environment, log_level) and parse LogsQueryResponse in frontend/src/services/api.ts
- [ ] T022 [US3] Build log search form: time range (start/end ISO or pickers), optional filters (service, environment, log_level), limit; use React Hook Form + Zod; submit triggers query in frontend/src/components/LogSearchForm.tsx
- [ ] T023 [US3] Build LogResults component: table or list of log records with timestamp_ns formatted via date-fns, raw_message, and label metadata (e.g. service, log_level) in frontend/src/components/LogResults.tsx
- [ ] T024 [US3] Use default time range (omit start/end so backend uses full extent of session logs); handle empty result with “no logs match” message; support limit and “load more” or pagination if applicable (FR-005) in frontend/src/components/LogSearchForm.tsx and frontend/src/components/LogResults.tsx
- [ ] T025 [US3] When session has no ingested logs, show empty or “no data” state and do not run query until user has uploaded logs (edge case from spec) in frontend

**Checkpoint**: User Story 3 complete — log search and inspection work

---

## Phase 6: User Story 4 — Metrics and Dashboards Access (Priority: P4)

**Goal**: Link that opens session-scoped metrics/dashboards (e.g. Grafana) in a new tab with session context; when session switches, clear way to open metrics for the new session; handle no-metrics state.

**Independent Test**: Select session with data, open metrics link in new tab and confirm session context; switch session and confirm link or instructions for new session; no data → clear message.

- [ ] T026 [US4] Build MetricsLink component: button or link that opens VITE_GRAFANA_URL in new tab with session context (e.g. query param var-session_id or dashboard variable) in frontend/src/components/MetricsLink.tsx
- [ ] T027 [US4] When user switches session, ensure MetricsLink or label clearly indicates “Open metrics for [current session]” or link updates with new session id (FR-006) in frontend/src/components/MetricsLink.tsx
- [ ] T028 [US4] When no metrics available for session (e.g. no data yet), show clear message or open link with empty-state guidance (FR-006) in frontend/src/components/MetricsLink.tsx

**Checkpoint**: User Story 4 complete — metrics/dashboard link works

---

## Phase 7: User Story 5 — Knowledge Base Ingest and Search (Priority: P5)

**Goal**: Trigger knowledge ingestion and see in-progress or complete status; on failure show brief reason; run knowledge search and display chunks with snippet and source metadata; empty state when no knowledge or ingest not run.

**Independent Test**: Trigger ingest, see status until idle; run search and verify snippets and source_path; empty knowledge → clear message.

- [ ] T029 [US5] Implement knowledge API: POST /knowledge/ingest, GET /knowledge/ingest/status, POST /knowledge/search in frontend/src/services/api.ts
- [ ] T030 [US5] Build useKnowledgeIngest hook: trigger ingest mutation, poll GET /knowledge/ingest/status until status is idle; show success/error via Sonner (FR-007) in frontend/src/hooks/useKnowledgeIngest.ts
- [ ] T031 [US5] Build KnowledgeIngest component: button to start ingest, display status (running / idle), last result or error message in frontend/src/components/KnowledgeIngest.tsx
- [ ] T032 [US5] Build useKnowledgeSearch hook and KnowledgeSearch component: search input, run query, display chunks (content, source_path, metadata) in frontend/src/hooks/useKnowledgeSearch.ts and frontend/src/components/KnowledgeSearch.tsx
- [ ] T033 [US5] When knowledge base is empty or ingest not run, show clear message (e.g. “Run ingestion first” or “No knowledge available”) in frontend/src/components/KnowledgeSearch.tsx (FR-007)

**Checkpoint**: User Story 5 complete — knowledge ingest and search work

---

## Phase 8: User Story 6 — Report Generation, Viewing, and Export (Priority: P6)

**Goal**: Trigger report generation with incident question; show “in progress” until content is ready; view full report; report history per session; export as Markdown or PDF when content ready; only one report generating at a time per session; export disabled until content available.

**Independent Test**: Select session with logs, enter question, trigger report, wait for content, view report, export Markdown and PDF; try second report while first generating → trigger disabled.

- [ ] T034 [US6] Implement reports API: GET /sessions/{id}/reports, GET /sessions/{id}/reports/{report_id}, POST /sessions/{id}/reports/generate, GET /sessions/{id}/reports/{report_id}/export?format=markdown|pdf (blob download) in frontend/src/services/api.ts
- [ ] T035 [US6] Build useReports hook: list reports, get report by id with polling until content is non-empty, generate mutation; invalidate list after generate in frontend/src/hooks/useReports.ts
- [ ] T036 [US6] Build ReportGenerate component: incident question input (React Hook Form + Zod), trigger button, disabled when a report is already generating for current session; show “in progress” until content (FR-008) in frontend/src/components/ReportGenerate.tsx
- [ ] T037 [US6] Build ReportList and ReportView: report history (list with created_at via date-fns), open report to view content (markdown rendered), export dropdown or buttons (Markdown / PDF) that trigger download (FR-009, FR-010) in frontend/src/components/ReportList.tsx and frontend/src/components/ReportView.tsx
- [ ] T038 [US6] Export only when report has content; show “generating…” or disable export and explain when content not ready (FR-010); one report at a time per session (FR-008) in frontend/src/components/ReportView.tsx
- [ ] T039 [US6] When user switches session during report generation, operation continues in original session; result visible when user returns to that session; UI does not cancel and makes behavior clear (FR-012) in frontend

**Checkpoint**: User Story 6 complete — report generation, view, and export work

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility, error handling, and validation of full flow

- [ ] T040 [P] Ensure keyboard navigation and logical focus order for main flows (session list and selection, upload, log search form, report trigger and view, export) per FR-013 in frontend/src/components/
- [ ] T041 [P] Add meaningful labels or aria attributes for screen readers on main interactive elements (buttons, links, form inputs) per FR-013 in frontend/src/components/
- [ ] T042 Ensure backend-unavailable and network errors show clear, user-friendly message and retry or “check connection” guidance (FR-011) in frontend (e.g. API client or global handler). Include retry/recovery UI where applicable (e.g. retry button or "Check connection" link) so users can recover without full reload.
- [ ] T043 Run quickstart.md validation: start backend and frontend, validate session list, create session, upload, log search, metrics link, knowledge ingest/search, report generate and export. Where applicable, confirm success criteria SC-001–SC-007 (e.g. session create+select in under one minute, clear upload result, export within typical time).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phases 3–8 (User Stories)**: Depend on Phase 2. US1 (Phase 3) is MVP; US2–US6 can proceed after Phase 2 in order or be parallelized by different developers
- **Phase 9 (Polish)**: Depends on completion of desired user stories

### User Story Dependencies

- **US1 (Session Management)**: No dependency on other frontend stories; required for US2–US6 (current session must exist)
- **US2 (Upload)**: Depends on US1 (current session)
- **US3 (Log Search)**: Depends on US1; benefits from US2 (data to search)
- **US4 (Metrics Link)**: Depends on US1 (current session for link context)
- **US5 (Knowledge)**: No dependency on US1–US4; can build in parallel
- **US6 (Reports)**: Depends on US1; benefits from US2 (logs) and US5 (knowledge) for richer reports

### Parallel Opportunities

- Within Phase 1: T003, T004, T005 can run in parallel after T001–T002
- Within Phase 2: T007 can run in parallel with T006; T008–T012 are largely independent after T006/T007
- After Phase 2: US2, US3, US4, US5 can be developed in parallel (different components); US6 after or in parallel with US2/US5
- Phase 9: T040, T041 can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Session Management)
4. **STOP and VALIDATE**: Create/list/select/edit sessions; confirm current session drives layout
5. Deploy or demo if ready

### Incremental Delivery

1. Phase 1 + 2 → foundation ready
2. Add US1 → Session management (MVP)
3. Add US2 → Upload and result
4. Add US3 → Log search
5. Add US4 → Metrics link
6. Add US5 → Knowledge ingest and search
7. Add US6 → Reports generate, view, export
8. Phase 9 → Polish and quickstart validation

### Parallel Team Strategy

After Phase 2:

- Developer A: US1 → US2 → US3 (session + upload + logs)
- Developer B: US4 + US5 (metrics link + knowledge)
- Developer C: US6 (reports)

---

## Notes

- [P] = parallelizable (different files, no blocking dependency)
- [USn] = task belongs to User Story n for traceability
- Each user story is independently testable per spec acceptance scenarios
- Frontend consumes existing backend API; no backend changes in this feature
- Commit after each task or logical group; validate at checkpoints
