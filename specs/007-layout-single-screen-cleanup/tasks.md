# Tasks: Single-Screen Layout, Pagination, and Copy Cleanup

**Input**: Design documents from `/specs/007-layout-single-screen-cleanup/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`, `backend/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add charts library and any shared tooling.

- [x] T001 Add recharts dependency to frontend in frontend/package.json
- [x] T002 [P] Use fixed batch size 10 for sessions list (no batch size control); was useBatchSize hook, removed per product decision

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No shared batch-size hook; batch size is fixed at 10 in each component.

**Checkpoint**: Complete Phase 1 (T001); then user story implementation can begin.

---

## Phase 3: User Story 1 - Single-Screen Session View (Priority: P1) — MVP

**Goal**: Main session view fits on one screen at desktop viewport; layout uses right-side space (grid); sessions list paginated with Load more + Previous; upload summary shown with Recharts.

**Independent Test**: Open session view at ≥1280×720; confirm Upload logs, Logs & metrics, Reports and Sessions sidebar fit without vertical scroll; confirm sessions show in batches with Load more/Previous; confirm upload result shows charts.

### Implementation for User Story 1

- [x] T003 [US1] Implement main content grid layout (CSS Grid, two columns at desktop) for Upload logs, Logs & metrics, Reports in frontend/src/App.tsx HomePage
- [x] T004 [US1] Add sessions list pagination (visibleCount state, Load more, optional Previous) with fixed batch size 10 in frontend/src/components/SessionList.tsx; hide or disable Load more and Previous when there are zero or only one page of sessions
- [x] T005 [US1] Batch size control removed; fixed at 10 per product decision
- [x] T006 [US1] Create UploadSummaryCharts component (Recharts: files processed/skipped, lines parsed/rejected, parsed coverage %) in frontend/src/components/UploadSummaryCharts.tsx
- [x] T007 [US1] Use UploadSummaryCharts in UploadLogs for success/partial result in frontend/src/components/UploadLogs.tsx

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Paginated Search Results (Priority: P2)

**Goal**: KB search results shown in batches with Load more and optional Previous; batch size selector (shared 10/20/50).

**Independent Test**: Run KB search with many results; confirm results in batches, Load more, Previous; confirm batch size control.

### Implementation for User Story 2

- [ ] T008 [US2] Add KB search results pagination (visibleCount/range, Load more, optional Previous) with fixed batch size 10 in frontend/src/components/KnowledgeSearch.tsx; hide or disable Load more and Previous when there are zero or only one page of results
- [x] T009 [US2] Batch size control removed; fixed at 10 per product decision (no dropdown for KB search)

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Back to Home Inside Knowledge Space (Priority: P3)

**Goal**: Back to Home control is inside the knowledge space content only; not in the global top nav on /knowledge.

**Independent Test**: Open /knowledge; confirm Back to Home is in the main content area; confirm it is not in the top nav; click returns to /.

### Implementation for User Story 3

- [ ] T010 [US3] Remove Back to Home from top nav when on /knowledge in frontend/src/components/AppLayout.tsx
- [ ] T011 [US3] Add Back to Home link/button at top of main content in frontend/src/components/KnowledgePage.tsx

**Checkpoint**: User Stories 1–3 work independently.

---

## Phase 6: User Story 4 - Reduced Repeated Copy and Icons (Priority: P4)

**Goal**: No redundant headings/copy; distinct icons for upload vs generate report.

**Independent Test**: Review Knowledge and session views; confirm single Knowledge base heading/description; confirm Upload and Generate report use different icons.

### Implementation for User Story 4

- [ ] T012 [P] [US4] Remove duplicate Knowledge base headings and redundant copy in frontend/src/components/KnowledgePage.tsx
- [ ] T013 [P] [US4] Use distinct icon for Generate report (e.g. FileOutput or Sparkles from lucide-react) in frontend/src/components/ReportGenerate.tsx; keep Upload icon for upload actions

**Checkpoint**: User Stories 1–4 work independently.

---

## Phase 7: User Story 5 - Top Bar Home Link and Application Icon (Priority: P5)

**Goal**: LogPilot in top bar is clickable and navigates to /; app icon (e.g. ScrollText) visible next to name.

**Independent Test**: Click LogPilot in top bar from any view → navigates to home; top bar shows app icon next to LogPilot.

### Implementation for User Story 5

- [ ] T014 [US5] Make LogPilot in top bar a link to / (e.g. React Router Link) in frontend/src/components/AppLayout.tsx
- [ ] T015 [US5] Add Lucide app icon (e.g. ScrollText) next to LogPilot with accessible label in frontend/src/components/AppLayout.tsx

**Checkpoint**: All user stories are independently functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validation and accessibility.

- [ ] T016 Run quickstart.md validation steps in specs/007-layout-single-screen-cleanup/quickstart.md
- [ ] T017 [P] Ensure pagination controls and charts have appropriate aria-labels and semantics per contracts/ui-pagination-and-charts.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately.
- **Phase 2**: Empty; T001–T002 complete before Phase 3.
- **Phase 3 (US1)**: Depends on T001.
- **Phase 4 (US2)**: No dependency on Phase 1 batch logic (fixed 10 in component).
- **Phase 5 (US3)**: No dependency on US1/US2; can start after Phase 2.
- **Phase 6 (US4)**: No dependency on other stories.
- **Phase 7 (US5)**: No dependency on other stories.
- **Phase 8 (Polish)**: Depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: After T001. Blocks nothing.
- **US2 (P2)**: Independent of US1; use fixed batch size 10 in KnowledgeSearch.
- **US3 (P3)**: Can start after Phase 2; touches AppLayout and KnowledgePage only.
- **US4 (P4)**: Can start after Phase 2; touches KnowledgePage and ReportGenerate only.
- **US5 (P5)**: Can start after Phase 2; touches AppLayout only.

### Parallel Opportunities

- T001 and T002 can run in parallel (Phase 1).
- After Phase 2: US3, US4, US5 can be done in parallel with each other; US1 and US2 can be done in parallel after T001–T002.
- T012 and T013 (US4) are [P] within the same phase (different files).

---

## Parallel Example: After Setup

```bash
# Option A: Sequential by priority
# T003 → T004 → T005 → T006 → T007 (US1)
# then T008 → T009 (US2)
# then T010 → T011 (US3), T012 → T013 (US4), T014 → T015 (US5)

# Option B: Parallel stories (different owners)
# Dev A: US1 (T003–T007)
# Dev B: US2 (T008–T009)
# Dev C: US3 (T010–T011)
# Dev D: US4 (T012–T013) — T012 and T013 can run in parallel
# Dev E: US5 (T014–T015)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: T001, T002.
2. Complete Phase 3: T003–T007 (single-screen layout, sessions pagination, upload charts).
3. **STOP and VALIDATE**: Run quickstart sections 1, 2, 6.
4. Deploy/demo if ready.

### Incremental Delivery

1. Phase 1 + Phase 3 → MVP (US1).
2. Add Phase 4 (US2) → validate KB pagination.
3. Add Phase 5 (US3) → validate Back to Home in content.
4. Add Phase 6 (US4) → validate copy/icons.
5. Add Phase 7 (US5) → validate top bar link and icon.
6. Phase 8 → full quickstart validation.

### Parallel Team Strategy

- After T001–T002: US1, US2, US3, US4, US5 can be assigned to different developers; only US1 and US2 share useBatchSize (no file conflicts).

---

## Notes

- [P] tasks use different files and have no ordering dependency within the phase.
- [Story] label maps each task to a user story for traceability.
- Spec does not require tests; no test tasks added.
- Commit after each task or logical group.
- Backend pagination (GET /sessions?limit=&offset=, KB search params) is optional per contracts; frontend implements client-side batching first.
