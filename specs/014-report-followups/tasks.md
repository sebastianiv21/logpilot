# Tasks: Report Follow-Up Improvements

**Input**: Design documents from `/specs/014-report-followups/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Include backend and frontend automated coverage for report metadata, copy behavior, and PDF export reliability because the plan explicitly calls for fixture-based regression coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` for FastAPI + SQLite, `frontend/` for Vite/React

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare report-focused test scaffolding and task execution baseline

- [ ] T001 Create report feature test skeleton files in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/tests/contract/test_api_reports.py`, `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/tests/unit/test_export.py`, and `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/tests/report-flow.test.tsx`
- [ ] T002 [P] Review and align report contract fixtures with `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/specs/014-report-followups/contracts/report-history-and-export.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core report-schema and API groundwork that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Update the SQLite reports schema and additive migration for persisted questions in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/app/lib/db.py`
- [ ] T004 Update the report domain model to carry question metadata in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/app/models/report.py`
- [ ] T005 Update report repository create/list/get helpers for question persistence and preview derivation in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/app/lib/repositories.py`
- [ ] T006 Update report API request/response models for history preview and detail question fields in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/app/api/reports.py`
- [ ] T007 [P] Update frontend report schemas for history preview and detail question fields in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/src/lib/schemas.ts`
- [ ] T008 [P] Update frontend report API client types for the expanded report payloads in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/src/services/api.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Report Includes Coding-Agent Fix Prompt (Priority: P1) 🎯 MVP

**Goal**: Ensure every full generated report includes a dedicated coding-agent fix prompt section that is preserved in full-report surfaces and exports

**Independent Test**: Generate a report and verify the full report view plus Markdown export contain a dedicated `Coding agent fix prompt` section aligned with the incident findings

### Tests for User Story 1

- [ ] T009 [P] [US1] Add backend contract coverage for report generation/detail responses with the new report section expectations in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/tests/contract/test_api_reports.py`
- [ ] T010 [P] [US1] Add backend unit coverage for Markdown export preserving the coding-agent fix prompt in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/tests/unit/test_export.py`
- [ ] T011 [P] [US1] Add backend unit coverage for coding-agent fix prompt alignment with evidence and uncertainty in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/tests/unit/test_agent.py`

### Implementation for User Story 1

- [ ] T012 [US1] Extend required report sections and prompt instructions for `Coding agent fix prompt` generation in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/app/services/agent.py`
- [ ] T013 [US1] Render the full report detail with the expanded section contract and optional incident-question context in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/src/components/ReportView.tsx`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Report History Shows Incident Questions (Priority: P1)

**Goal**: Show a scannable incident-question preview in report history with access to the full question on demand while keeping history rows lightweight

**Independent Test**: Generate multiple reports for one session and confirm the history list shows readable question previews, distinguishes runs, and handles legacy rows without question metadata

### Tests for User Story 2

- [ ] T014 [P] [US2] Add backend contract coverage for report list history preview fields and legacy fallback behavior in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/tests/contract/test_api_reports.py`
- [ ] T015 [P] [US2] Add frontend interaction coverage for report history preview rendering and on-demand full question display in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/tests/report-flow.test.tsx`

### Implementation for User Story 2

- [ ] T016 [US2] Implement question preview derivation and legacy-safe history access in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/app/lib/repositories.py`
- [ ] T017 [US2] Return question preview and `has_question` metadata from the report list endpoint in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/app/api/reports.py`
- [ ] T018 [US2] Update report list query typing and caching for the new history metadata in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/src/hooks/useReports.ts`
- [ ] T019 [US2] Render report history previews and on-demand question context without surfacing the coding-agent prompt in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/src/components/ReportList.tsx`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Rendered Report Supports Quick Copy (Priority: P2)

**Goal**: Add a compact report copy control that copies Markdown from the full report viewport and provides clear success/failure feedback

**Independent Test**: Open a rendered report, use the copy control, and verify pasted output preserves Markdown structure while copy failures surface an accessible error

### Tests for User Story 3

- [ ] T020 [P] [US3] Add frontend coverage for report copy success and clipboard failure feedback in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/tests/report-flow.test.tsx`

### Implementation for User Story 3

- [ ] T021 [US3] Add a compact report copy control using the session-ID interaction pattern in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/src/components/ReportView.tsx`
- [ ] T022 [US3] Ensure report detail data loading exposes the exact Markdown content required for clipboard copy in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/src/hooks/useReports.ts`

**Checkpoint**: At this point, User Stories 1, 2, and 3 should all work independently

---

## Phase 6: User Story 4 - PDF Export Produces a Usable Report (Priority: P2)

**Goal**: Make PDF export reliable for full report content, including long questions, the new coding-agent prompt section, ordered steps, and mixed code/prose blocks

**Independent Test**: Export representative reports as PDF and confirm successful generation plus readable output; simulate export failure and confirm the UI surfaces a clear error

### Tests for User Story 4

- [ ] T023 [P] [US4] Add backend unit fixtures covering long question text, coding-agent prompt sections, ordered steps, and code blocks in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/tests/unit/test_export.py`
- [ ] T024 [P] [US4] Add frontend coverage for PDF export failure messaging in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/tests/report-flow.test.tsx`
- [ ] T025 [US4] Define a representative PDF export fixture matrix and pass criteria for SC-004 in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/specs/014-report-followups/quickstart.md`

### Implementation for User Story 4

- [ ] T026 [US4] Harden PDF export flowables and failure handling for expanded report content in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/app/services/export.py`
- [ ] T027 [US4] Keep the export endpoint failure mapping stable and user-friendly for PDF failures in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/app/api/reports.py`
- [ ] T028 [US4] Align report export UI states and messages with the hardened backend behavior in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/src/components/ReportView.tsx`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and validation across all stories

- [ ] T029 [P] Document report follow-up validation notes and execution steps in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/specs/014-report-followups/quickstart.md`
- [ ] T030 Run frontend and backend automated checks for the feature from `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend` and `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend`
- [ ] T031 Run the end-to-end manual validation flow for report generation, history preview, copy, and export using `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/specs/014-report-followups/quickstart.md`
- [ ] T032 Record PDF export fixture-matrix pass/fail results against the SC-004 acceptance threshold in `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/specs/014-report-followups/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and benefits from US1 report-question persistence
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can build on US1 report detail behavior
- **User Story 4 (Phase 6)**: Depends on Foundational completion and should be completed after US1 so the export path covers the final report contract
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts first after Foundational - establishes the full report contract and persisted question metadata
- **User Story 2 (P1)**: Depends on foundational report metadata support but remains independently testable once history responses are implemented
- **User Story 3 (P2)**: Depends on full report detail data being available; otherwise independent
- **User Story 4 (P2)**: Depends on the final full-report content shape from US1 and remains independently testable through export flows

### Within Each User Story

- Tests for the story should be written before or alongside implementation and fail against the missing behavior
- Backend contract/model changes should land before frontend consumers for that story
- Story UI changes should follow the API/data-shape work they depend on

### Parallel Opportunities

- T002 can run in parallel with T001
- T007 and T008 can run in parallel after T006 is defined
- T009 and T010 can run in parallel for US1
- T014 and T015 can run in parallel for US2
- T023 and T024 can run in parallel for US4
- Once Phase 2 completes, US2 and US3 can proceed in parallel with US1 finishing if team capacity allows, but US4 should wait for the US1 report contract changes

---

## Parallel Example: User Story 2

```bash
# Launch history-focused tests together:
Task: "Add backend contract coverage for report list history preview fields and legacy fallback behavior in /Users/sebastianiv21/Documents/projects/appsmith/logpilot/backend/tests/contract/test_api_reports.py"
Task: "Add frontend interaction coverage for report history preview rendering and on-demand full question display in /Users/sebastianiv21/Documents/projects/appsmith/logpilot/frontend/tests/report-flow.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Generate a report and confirm the new `Coding agent fix prompt` section appears in the full report and Markdown export

### Incremental Delivery

1. Complete Setup + Foundational to establish persisted question metadata and API shape
2. Add User Story 1 for the new full-report contract
3. Add User Story 2 for report history context
4. Add User Story 3 for viewport copy
5. Add User Story 4 for PDF export reliability
6. Finish with polish and full quickstart validation

### Parallel Team Strategy

1. One developer handles Phase 2 backend schema/API groundwork
2. After foundation:
   - Developer A: User Story 1 backend prompt/detail work
   - Developer B: User Story 2 history list UI/API integration
   - Developer C: User Story 3 copy interaction
3. Bring User Story 4 in once the final report content shape is stable

---

## Notes

- [P] tasks target different files and can be worked independently
- [US1] through [US4] map directly to the stories in [spec.md](/Users/sebastianiv21/Documents/projects/appsmith/logpilot/specs/014-report-followups/spec.md)
- Every task includes an exact file path and is specific enough for direct execution
- Use `/Users/sebastianiv21/Documents/projects/appsmith/logpilot/specs/014-report-followups/quickstart.md` as the final manual verification checklist
