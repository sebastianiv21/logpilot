# Tasks: Knowledge base config route and layout improvements

**Input**: Design documents from `/specs/005-kb-config-route-layout/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for components, hooks, App, routes

---

## Phase 1: Foundation (Route + layout structure)

**Purpose**: Add the `/knowledge` route and a main-content navbar in AppLayout so the upper-right control has a destination and a place to live. Unblocks US1 and US2.

- [x] T001 Add `/knowledge` route and `KnowledgePage` component in `frontend/src/App.tsx`; render `KnowledgeIngest` and `KnowledgeSearch` inside `frontend/src/components/KnowledgePage.tsx`, grouped under a single "Knowledge base" heading per spec.
- [x] T002 Add a main-content navbar (horizontal bar above the page content) in `frontend/src/components/AppLayout.tsx` so the main area has a top-right region for the KB control; ensure `Outlet` remains below the navbar and skip-link/main landmarks are preserved.

**Checkpoint**: Navigating to `/knowledge` shows the KB page; AppLayout has a navbar for the control.

---

## Phase 2: User Story 1 — Open knowledge base from upper-right control (Priority: P1) — MVP

**Goal**: User sees database icon + status indicator (red/yellow/green) in the upper-right; single click navigates to the knowledge page; tooltip "Knowledge base"; main screen no longer shows the KB block.

**Independent Test**: On home, see icon + indicator and tooltip; click to open knowledge page; confirm home does not show ingestion/search block.

### Implementation for User Story 1

- [x] T003 [US1] Create `frontend/src/components/HeaderKbLink.tsx`: database icon (lucide-react `Database`) + status indicator dot (red when idle and no last_result or error; yellow/ochre with pulsating CSS when status === 'running'; green when idle with last_result and no error). Use `useKnowledgeIngestStatus` from `frontend/src/hooks/useKnowledgeIngest.ts` for state. Single click navigates to `/knowledge` (React Router `Link` or `useNavigate`). Tooltip "Knowledge base" on hover/focus (title or a proper tooltip). aria-label that includes status for assistive tech (e.g. "Knowledge base, no data" / "Knowledge base, ingesting" / "Knowledge base, ready").
- [x] T004 [US1] In `frontend/src/components/AppLayout.tsx`, render `HeaderKbLink` in the top-right of the main-content navbar (from T002). Ensure it is keyboard-focusable and visible on both home and knowledge routes.
- [x] T005 [US1] Remove the knowledge base section (KnowledgeIngest + KnowledgeSearch) from the home page in `frontend/src/App.tsx` (or the component that renders the main content for `/`), so the main screen shows only intro, Upload logs, Logs & metrics, Reports in that order.

**Checkpoint**: User Story 1 is independently testable; upper-right control works and main screen has no KB block.

---

## Phase 3: User Story 2 — Knowledge base on its own route (Priority: P2)

**Goal**: Knowledge page is reachable via direct URL and bookmark; in-app return control ("Back to home" or "Home") plus browser back work.

**Independent Test**: Open `/knowledge` directly; use in-app return and browser back; bookmark and reopen.

### Implementation for User Story 2

- [ ] T006 [US2] Add a visible in-app return control (e.g. "Back to home" or "Home" link or button) on the knowledge page. Prefer placing it at the top of `KnowledgePage` or in the same AppLayout navbar when on `/knowledge` (e.g. left side of navbar) so it is above the KB section. Link to `/` using React Router `Link`.
- [ ] T007 [US2] Verify direct navigation to `/knowledge` (e.g. address bar, bookmark) renders the knowledge page without errors and without requiring a session (KB is global). Verify browser back from `/knowledge` returns to the previous screen. (Manual validation; also covered by T011 quickstart.)

**Checkpoint**: User Story 2 is independently testable; route is bookmarkable and return control works.

---

## Phase 4: User Story 3 — Improved layout and information hierarchy (Priority: P3)

**Goal**: Main screen and knowledge screen have clear headings, spacing, and grouping; section order on main unchanged (intro, upload logs, logs & metrics, reports).

**Independent Test**: Scan both screens; confirm hierarchy is clear and "session work" vs "knowledge base" are distinguishable.

### Implementation for User Story 3

- [ ] T008 [US3] In the home page content (e.g. in `frontend/src/App.tsx` or the component for `/`), ensure sections have clear visual hierarchy: consistent heading levels (e.g. h1 for title, h2 for section titles), spacing (e.g. `space-y-6`, `border-t`, `pt-6` between major sections), and grouping. Do not change the order of sections.
- [ ] T009 [US3] In `frontend/src/components/KnowledgePage.tsx`, ensure knowledge base ingestion and search are grouped under one coherent section with a clear heading and spacing so it is obvious they belong together. Optionally add a short descriptive line under the heading.

**Checkpoint**: User Story 3 is independently testable; layout is clearer on both screens.

---

## Phase 5: Polish & validation

**Purpose**: Accessibility and quickstart validation

- [ ] T010 Ensure status indicator pulsating effect for "in progress" (yellow/ochre) is implemented (e.g. Tailwind `animate-pulse` or custom keyframes) in `frontend/src/components/HeaderKbLink.tsx`.
- [ ] T011 Run the validation steps in `specs/005-kb-config-route-layout/quickstart.md` (upper-right control, tooltip, navigation, return link, main screen without KB, direct URL, keyboard/accessibility).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundation)**: No dependencies — start here. Delivers route and header structure.
- **Phase 2 (US1)**: Depends on Phase 1 (need `/knowledge` route and header area). Delivers upper-right control and removal of KB from home.
- **Phase 3 (US2)**: Depends on Phase 1 (need KnowledgePage). Return link can be added in Phase 2 or 3; T006 is independent of T003–T005 once T001 is done.
- **Phase 4 (US3)**: Can be done after Phase 2/3; improves layout on existing pages.
- **Phase 5**: After all implementation tasks.

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 1 only. Delivers MVP: control + no KB on home.
- **US2 (P2)**: Depends on Phase 1; return link and URL behavior complete the story.
- **US3 (P3)**: Can follow US1/US2; layout polish only.

### Parallel Opportunities

- T003 (HeaderKbLink) and T005 (remove KB from home) can be done in either order once T001–T002 are done; T004 (render in AppLayout) depends on T003.
- T008 and T009 (layout) can be done in parallel.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 (T001–T002).
2. Complete Phase 2 (T003–T005).
3. Validate: upper-right control, tooltip, navigate to `/knowledge`, main screen without KB.

### Incremental Delivery

1. Phase 1 → Phase 2 → Validate US1 (MVP).
2. Phase 3 → Validate US2 (return + direct URL).
3. Phase 4 → Validate US3 (layout).
4. Phase 5 → Quickstart and a11y check.

---

## Notes

- Route path is `/knowledge` per research.md.
- Status indicator uses existing `GET /knowledge/ingest/status`; no backend changes.
- Failed ingestion shows red (same as no KB) per spec clarification.
- [P] tasks = different files or independent steps where safe.
