# Tasks: Session Search Bar

**Input**: Design documents from `/specs/009-session-search-bar/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included.

**Organization**: Tasks are grouped by user story (US1: search by name/ID/link, US2: empty state) and cross-cutting a11y to allow independent implementation and validation.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files or no dependencies)
- **[Story]**: User story (US1, US2) or cross-cutting (A11y)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for components, hooks; `backend/` unchanged for this feature

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm environment; add debounce hook per research.md (no new npm packages required).

- [x] T001 Verify frontend dependencies per plan.md; no new packages required for 009 (debounce implemented via small hook)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Debounce hook required so search filter and live region update after 150–300 ms pause.

**Checkpoint**: Hook available; US1 implementation can use it.

- [x] T002 [US1] Add useDebouncedValue hook (delay e.g. 200 ms) in frontend/src/hooks/useDebouncedValue.ts; input (value, delayMs), output debounced value per research.md §1

---

## Phase 3: User Story 1 - Search Sessions by Name, ID, or External Link (Priority: P1) MVP

**Goal**: User can type in a search bar; list shows only sessions matching the text (case-insensitive substring on name, ID, or external link). Input trimmed; empty/whitespace-only shows full list. List updates after short debounce. Clearing search restores full list.

**Independent Test**: Load app with multiple sessions; enter text in search bar; after pause, only matching sessions shown. Clear input; full list returns. See quickstart.md §2–3, §5.

### Implementation for User Story 1

- [x] T003 [US1] In SessionList, add optional prop searchQuery (string); when present and non-empty after trim, filter sessions by literal case-insensitive substring match (no regex) on session.name ?? '', session.id, session.external_link ?? ''; when empty after trim, show all sessions. Pagination (visibleCount, Load more) applies to filtered list. In frontend/src/components/SessionList.tsx
- [x] T004 [US1] In AppLayout, add search input in a new block directly above the scrollable session list (between CreateSessionForm and the div with overflow-y-auto), same column; wire local state for raw input, useDebouncedValue(rawInput.trim(), 200), pass debounced value to SessionList as searchQuery. Keep scroll region (flex-1 min-h-0 overflow-y-auto) wrapping only SessionList. In frontend/src/components/AppLayout.tsx

**Checkpoint**: User Story 1 complete — search filters list by name/ID/link, trim and debounce work; validate per quickstart §2–3, §5

---

## Phase 4: User Story 2 - Clear Empty State When No Matches (Priority: P2)

**Goal**: When at least one session exists but none match the current search, show a clear message (e.g. "No sessions match your search") so the user knows the result is from the filter.

**Independent Test**: Enter text that matches no session; after debounce, see "No sessions match your search". Clear search; full list returns. See quickstart.md §4.

### Implementation for User Story 2

- [x] T005 [US2] In SessionList, when sessions.length > 0 but filtered list is empty (searchQuery non-empty after trim and no matches), render empty state message "No sessions match your search" (or equivalent) instead of empty list; keep existing "No sessions yet" when sessions.length === 0. In frontend/src/components/SessionList.tsx

**Checkpoint**: User Story 2 complete — empty state when no matches; validate per quickstart §4

---

## Phase 5: Accessibility (Cross-Cutting)

**Purpose**: Spec FR-007 — accessible label for search input and live region for filter result.

- [x] T006 [A11y] Give the session search input an accessible name (e.g. aria-label="Search sessions by name, ID, or link") in frontend/src/components/AppLayout.tsx
- [x] T007 [A11y] Add a live region (aria-live="polite", aria-atomic="true") that announces the filter result when the debounced search changes: when filter is active (searchQuery non-empty), announce number of matching sessions (e.g. "3 sessions" or "1 session") or "No sessions match your search" when filtered list is empty; when search is empty, omit or keep announcement minimal to avoid noise. Place in SessionList so it has access to filtered count and searchQuery; update region text when filtered result changes. In frontend/src/components/SessionList.tsx

**Checkpoint**: Search input has label; screen reader hears result count or "no sessions match"; validate per quickstart §6

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation and final checks

- [ ] T008 Run quickstart.md validation steps for 009 in specs/009-session-search-bar/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: None — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — debounce hook
- **Phase 3 (US1)**: Depends on Phase 2 (hook); T003 (filter in SessionList) can be done before or with T004 (AppLayout adds input and passes query)
- **Phase 4 (US2)**: Depends on US1 (filtered list exists); add empty state in SessionList
- **Phase 5 (A11y)**: Depends on US1 (search input and filtered list exist); T006 in AppLayout, T007 in SessionList
- **Phase 6 (Polish)**: Depends on US1, US2, A11y complete

### User Story Dependencies

- **US1 (P1)**: No dependency on US2 — implement first for MVP
- **US2 (P2)**: Builds on US1 (filtered list); add empty-state branch in SessionList
- **A11y**: Builds on US1 (input + filter); add label and live region

### Within Each Phase

- Phase 2: T002 only
- Phase 3: T003 (SessionList filter) then T004 (AppLayout input + state + pass query); or T004 after T003 in same branch
- Phase 4: T005 (empty state in SessionList)
- Phase 5: T006 (label) and T007 (live region) can be done in either order or together

### Parallel Opportunities

- T006 and T007 are in different files (AppLayout vs SessionList); can be done in parallel after US1/US2
- T003 and T004: T003 must be done so SessionList accepts searchQuery before T004 passes it; sequential in practice unless SessionList is stubbed

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002)
3. Complete Phase 3: User Story 1 (T003, T004)
4. **STOP and VALIDATE**: Quickstart §1–3, §5 — search filters list; debounce and trim work
5. Deploy/demo if ready

### Incremental Delivery

1. Add US1 → validate search, debounce, clear
2. Add US2 → validate "No sessions match your search" when no matches
3. Add A11y (T006, T007) → validate label and live region
4. Run full quickstart (T008)

### Optional Refactor

- If sidebar grows, extract a `SessionSidebar` component (heading + Create form + search input + scroll region with SessionList) and use it in AppLayout; contracts in specs/009-session-search-bar/contracts/ui-session-search-bar.md.

---

## Notes

- [P] tasks: T006, T007 can run in parallel (different files)
- [Story] label links each task to US1/US2/A11y for traceability
- No backend or new routes; frontend-only in frontend/src
- SessionList receives searchQuery from AppLayout; filter and empty state live in SessionList
- Commit after each task or after each checkpoint
