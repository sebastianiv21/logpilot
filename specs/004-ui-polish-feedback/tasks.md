# Tasks: UI polish — icons, copy, loading cues, report-ready feedback

**Input**: Design documents from `/specs/004-ui-polish-feedback/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for components, contexts, lib, assets; `frontend/public/` for static assets if needed.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependencies and shared utilities for the feature

- [x] T001 Add lucide-react dependency to frontend/package.json (install and verify)
- [x] T002 [P] Add report-ready sound asset at frontend/public/report-ready.ogg and create playReportReadySound with throttle/queue in frontend/src/lib/sound.ts
- [x] T003 Create report-ready notification helper (toast.success with context-aware message + playReportReadySound) in frontend/src/lib/reportReadyNotification.ts; ensure sound is throttled/queued when multiple reports ready in quick succession (per contracts/report-ready-notification.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None required for this feature beyond Setup. All user stories can start after Phase 1.

**Checkpoint**: Setup complete — user story implementation can begin

---

## Phase 3: User Story 1 — Clear visual feedback when content is loading (Priority: P1) — MVP

**Goal**: Users see clear visual loading indicators (spinner, skeleton, or progress cue) for all major async operations, with aria-busy/role="status" where appropriate.

**Independent Test**: Trigger any async operation (open app, open report, upload, ingest, generate report). Confirm loading is indicated with visible cues, not only plain "Loading…" text.

### Implementation for User Story 1

- [x] T004 [P] [US1] Add visual loading indicator (spinner or skeleton) and aria-busy/role="status" in frontend/src/components/SessionList.tsx
- [x] T005 [P] [US1] Add visual loading indicator (spinner or skeleton) and aria-busy/role="status" in frontend/src/components/ReportList.tsx
- [x] T006 [P] [US1] Add visual loading indicator (spinner or skeleton) and aria-busy/role="status" in frontend/src/components/ReportView.tsx
- [x] T007 [P] [US1] Add or ensure visual loading indicator for "Load more" and aria-busy in frontend/src/components/LogResults.tsx
- [x] T008 [P] [US1] Add or ensure visual loading indicator and aria-busy in frontend/src/components/KnowledgeIngest.tsx
- [x] T009 [P] [US1] Ensure visible loading state and aria-busy in frontend/src/components/ReportGenerate.tsx
- [x] T010 [P] [US1] Add visual loading indicator (e.g. spinner) when checking connection in frontend/src/components/ConnectionBanner.tsx
- [x] T011 [P] [US1] Ensure visible loading (spinner) and aria-busy in frontend/src/components/CreateSessionForm.tsx and frontend/src/components/EditSessionForm.tsx
- [x] T012 [P] [US1] Ensure visible loading and aria-busy for search actions in frontend/src/components/LogSearchForm.tsx and frontend/src/components/KnowledgeSearch.tsx
- [x] T013 [US1] Verify frontend/src/components/UploadLogs.tsx has visible spinner and aria-busy/role="status" (enhance if needed)

**Checkpoint**: User Story 1 is independently testable; all major async flows show clear loading cues.

---

## Phase 4: User Story 2 — Notification and sound when report is ready (Priority: P1)

**Goal**: When a report transitions from generating to ready, show a toast and play a subtle sound once (throttled when multiple reports ready in quick succession).

**Independent Test**: Start report generation, optionally switch session/tab. When report content is ready, a toast appears and a short, subtle sound plays.

### Implementation for User Story 2

- [x] T014 [US2] In frontend/src/contexts/ReportGenerationContext.tsx, when poll detects report content ready, call report-ready notification helper (toast + sound) before clearing that session from generatingBySession
- [x] T015 [US2] Ensure report-ready toast message is context-aware: include session name or id when multiple sessions have reports generating (per contracts/report-ready-notification.md); resolve session label via getSession(sessionId) from frontend/src/services/api.ts when building the message (Session has name and id)

**Checkpoint**: User Story 2 is independently testable; report ready triggers toast and subtle sound (sound best-effort for accessibility).

---

## Phase 5: User Story 3 — Consistent, appropriate use of icons (Priority: P2)

**Goal**: Icons (lucide-react) appear on key actions and section headings where they add clarity; consistent style and size; not overused.

**Independent Test**: Browse sessions, reports, log search, knowledge search, upload, report generate. Key actions/sections have appropriate icons; density is moderate.

### Implementation for User Story 3

- [x] T016 [P] [US3] Add lucide-react icons to frontend/src/components/AppLayout.tsx (sessions section, nav)
- [x] T017 [P] [US3] Add lucide-react icons to frontend/src/components/SessionList.tsx for session-related actions
- [x] T018 [P] [US3] Add lucide-react icons to frontend/src/components/ReportList.tsx and frontend/src/components/ReportView.tsx (reports, export actions)
- [x] T019 [P] [US3] Add lucide-react icons to frontend/src/components/UploadLogs.tsx and frontend/src/components/ReportGenerate.tsx
- [x] T020 [P] [US3] Add lucide-react icons to frontend/src/components/KnowledgeIngest.tsx and frontend/src/components/KnowledgeSearch.tsx
- [x] T021 [P] [US3] Add lucide-react icons to frontend/src/components/LogSearchForm.tsx and frontend/src/components/ConnectionBanner.tsx
- [x] T022 [P] [US3] Add lucide-react icons to frontend/src/components/CreateSessionForm.tsx and frontend/src/components/EditSessionForm.tsx
- [x] T023 [US3] Use consistent icon size (e.g. size={18} or className w-4 h-4) across all icon usages in frontend/src/components

**Checkpoint**: User Story 3 is independently testable; icons are consistent and purposeful.

---

## Phase 6: User Story 4 — Clearer, simpler platform copy (Priority: P2)

**Goal**: All user-facing text (headings, buttons, placeholders, toasts, errors, empty states, loading messages) is concise, consistent, and non-technical where possible.

**Independent Test**: Review all main app strings; confirm wording is simplified and consistent (per spec FR-004 and Clarifications scope).

### Implementation for User Story 4

- [ ] T024 [P] [US4] Review and simplify copy in frontend/src/App.tsx and frontend/src/components/AppLayout.tsx
- [ ] T025 [P] [US4] Review and simplify copy in frontend/src/components/SessionList.tsx, frontend/src/components/CreateSessionForm.tsx, frontend/src/components/EditSessionForm.tsx
- [ ] T026 [P] [US4] Review and simplify copy in frontend/src/components/ReportList.tsx, frontend/src/components/ReportView.tsx, frontend/src/components/ReportGenerate.tsx
- [ ] T027 [P] [US4] Review and simplify copy in frontend/src/components/LogSearchForm.tsx, frontend/src/components/LogResults.tsx, frontend/src/components/KnowledgeIngest.tsx, frontend/src/components/KnowledgeSearch.tsx
- [ ] T028 [P] [US4] Review and simplify copy in frontend/src/components/UploadLogs.tsx and frontend/src/components/ConnectionBanner.tsx
- [ ] T029 [US4] Simplify toast and error messages across components (ReportGenerate, ReportView, KnowledgeIngest, UploadLogs, ConnectionBanner) per spec FR-004; prefer non-technical messages (e.g. "Check your connection")

**Checkpoint**: User Story 4 is independently testable; copy is shorter and clearer across the app.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation and final checks

- [ ] T030 Run quickstart validation per specs/004-ui-polish-feedback/quickstart.md and fix any regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately. T002 and T003 can follow T001.
- **Foundational (Phase 2)**: None for this feature.
- **User Story 1 (Phase 3)**: Depends on Phase 1 (lucide-react optional for US1; loading does not require it). All US1 tasks marked [P] can run in parallel.
- **User Story 2 (Phase 4)**: Depends on Phase 1 (T003 notification helper). T014 and T015 are sequential (integrate in context, then add context-aware message).
- **User Story 3 (Phase 5)**: Depends on Phase 1 (T001 lucide-react). US3 tasks can run in parallel after T023 (consistency pass) at end.
- **User Story 4 (Phase 6)**: No dependency on other stories. All US4 tasks marked [P] can run in parallel.
- **Polish (Phase 7)**: Depends on completion of desired user stories.

### User Story Dependencies

- **User Story 1 (P1)**: After Setup — no dependency on US2, US3, US4.
- **User Story 2 (P1)**: After Setup (T003) — no dependency on US1, US3, US4.
- **User Story 3 (P2)**: After Setup (T001) — no dependency on US1, US2, US4.
- **User Story 4 (P2)**: Can run anytime after Setup — no dependency on US1, US2, US3.

### Parallel Opportunities

- Phase 1: T002 [P] can run after T001 (T003 depends on T002).
- Phase 3: T004–T012 [P] can run in parallel; T013 is a single verification.
- Phase 4: T014 then T015 (sequential).
- Phase 5: T016–T022 [P] can run in parallel; T023 is consistency pass.
- Phase 6: T024–T028 [P] can run in parallel; T029 touches multiple components.
- US1 and US2 can be implemented in parallel by different developers after Setup; US3 and US4 can also run in parallel with each other and with US1/US2.

---

## Parallel Example: User Story 1

```text
# All loading-indicator tasks can run in parallel (different files):
T004 SessionList.tsx
T005 ReportList.tsx
T006 ReportView.tsx
T007 LogResults.tsx
T008 KnowledgeIngest.tsx
T009 ReportGenerate.tsx
T010 ConnectionBanner.tsx
T011 CreateSessionForm.tsx, EditSessionForm.tsx
T012 LogSearchForm.tsx, KnowledgeSearch.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup (T001–T003).
2. Complete Phase 3: User Story 1 (loading indicators).
3. Complete Phase 4: User Story 2 (report-ready toast + sound).
4. **STOP and VALIDATE**: Run quickstart sections 1 and 2.
5. Deploy or continue with P2 stories.

### Incremental Delivery

1. Setup → US1 (loading) → validate → MVP usability improvement.
2. US2 (report ready) → validate → full P1 done.
3. US3 (icons) → validate.
4. US4 (copy) → validate.
5. Polish (T030) → done.

### Parallel Team Strategy

- Developer A: Phase 1 then US1 (loading).
- Developer B: Phase 1 then US2 (report-ready) after T003.
- Developer C: Phase 1 then US3 (icons) and US4 (copy) in any order.

---

## Notes

- [P] tasks use different files and have no ordering dependency within the same phase.
- [USn] maps each task to a user story for traceability.
- Each user story can be completed and validated independently per quickstart.md.
- No test tasks were added; spec did not request TDD or explicit test tasks.
- Commit after each task or logical group; run quickstart after each story to confirm no regressions.
