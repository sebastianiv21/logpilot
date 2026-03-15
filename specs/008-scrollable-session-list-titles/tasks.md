# Tasks: Scrollable Session List and Dynamic Session Titles with Copy ID

**Input**: Design documents from `/specs/008-scrollable-session-list-titles/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included.

**Organization**: Tasks are grouped by user story (US1: scrollable list, US2: dynamic titles, US3: session ID + copy) to allow independent implementation and validation.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files or no dependencies)
- **[Story]**: User story (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for components, hooks, App; `backend/` unchanged for this feature

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm environment and dependencies; no new packages required per plan.

- [x] T001 Verify frontend dependencies (Sonner, lucide-react) per plan.md; no new packages required for 008

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None required for this feature — existing SessionContext, useSessionsList, and AppLayout are sufficient. Proceed to Phase 3.

**Checkpoint**: Setup complete; user story implementation can begin

---

## Phase 3: User Story 1 - Self-Contained Scrollable Session List (Priority: P1) MVP

**Goal**: The session list in the sidebar scrolls inside its own region; scrolling the list does not scroll the rest of the page (Upload logs, Logs & metrics, Reports).

**Independent Test**: Open main view with enough sessions to overflow the list area; scroll inside the session list; confirm only the list scrolls and main content stays fixed. See quickstart.md §1.

### Implementation for User Story 1

- [x] T002 [US1] Add scrollable wrapper (flex-1 min-h-0 overflow-y-auto) around SessionList in AppLayout so only the list scrolls per contracts/ui-sidebar-scroll-region.md in frontend/src/components/AppLayout.tsx
- [x] T003 [US1] Ensure Sessions heading, Current line, and CreateSessionForm remain outside the scroll region in frontend/src/components/AppLayout.tsx

**Checkpoint**: User Story 1 complete — session list scrolls independently; validate per quickstart §1

---

## Phase 4: User Story 2 - Dynamic Section Titles with Current Session (Priority: P2)

**Goal**: Logs & metrics and Reports section titles show the current session name, or "Session " + first 8 chars of ID, or "No session selected"; long names truncated with ellipsis and full name on hover.

**Independent Test**: Select a session with a name and one without; confirm both section titles update. Clear selection and confirm placeholder. See quickstart.md §2–3.

### Implementation for User Story 2

- [ ] T004 [US2] Derive currentSession (Session | null) in HomePage from useSessionsList().data?.sessions and useCurrentSession().currentSessionId in frontend/src/App.tsx
- [ ] T005 [US2] Replace static "Logs & metrics" and "Reports" h2 with dynamic title (session name, or "Session " + id.slice(0,8), or "No session selected") in frontend/src/App.tsx
- [ ] T006 [P] [US2] Add truncation (e.g. truncate class) and full name on hover (title attribute) for section titles when session name is too long to fit in frontend/src/App.tsx

**Checkpoint**: User Story 2 complete — section titles reflect current session; validate per quickstart §2–3

---

## Phase 5: User Story 3 - Full Session ID with Copy (Priority: P3)

**Goal**: Full session ID visible below each section title with a copy button; success/error toast feedback; accessible name for copy control; ID line and copy hidden when no session.

**Independent Test**: Select a session; confirm full ID and copy button below both section titles; click copy and paste elsewhere; confirm success toast. See quickstart.md §4–5.

### Implementation for User Story 3

- [ ] T007 [US3] Add session ID line (full session.id) and copy button below Logs & metrics and Reports section titles, visible only when currentSession is non-null in frontend/src/App.tsx
- [ ] T008 [US3] Implement copy handler with navigator.clipboard.writeText(sessionId), Sonner success toast (e.g. "Session ID copied") and error toast (e.g. "Copy failed"), and button aria-label "Copy session ID" in frontend/src/App.tsx

**Checkpoint**: User Story 3 complete — session ID copy with feedback; validate per quickstart §4–5

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation and final checks

- [ ] T009 Run quickstart.md validation steps for 008 in specs/008-scrollable-session-list-titles/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: None — start immediately
- **Phase 2 (Foundational)**: None for this feature
- **Phase 3 (US1)**: Depends on Phase 1 — scroll region in AppLayout
- **Phase 4 (US2)**: Depends on Phase 1; can follow US1 (no hard dependency on US1)
- **Phase 5 (US3)**: Depends on US2 (section titles and currentSession exist); add ID line and copy to same sections
- **Phase 6 (Polish)**: Depends on US1, US2, US3 complete

### User Story Dependencies

- **US1 (P1)**: No dependency on US2/US3 — implement first for MVP
- **US2 (P2)**: No dependency on US1; needs currentSession in HomePage
- **US3 (P3)**: Builds on US2 (same section headers); add ID line and copy below titles

### Within Each User Story

- US1: T002 then T003 (same file, layout order)
- US2: T004 (derive session) then T005 (titles) then T006 (truncation)
- US3: T007 (ID line + button) then T008 (handler + toast + aria-label)

### Parallel Opportunities

- T006 [P] can be done in same pass as T005 (same file) or immediately after
- US1 and US2 could be started in parallel by different developers (different files: AppLayout vs App.tsx) after Setup
- US3 must follow US2 (same sections in App.tsx)

---

## Parallel Example: User Story 1

```bash
# Single developer: T002 then T003 in frontend/src/components/AppLayout.tsx
# (Same file; wrapper then verify header/form outside.)
```

## Parallel Example: User Story 2

```bash
# After T004: T005 (dynamic title) and T006 (truncation + title) can be one edit in frontend/src/App.tsx
```

## Parallel Example: User Story 3

```bash
# T007 add UI; T008 add behavior (same file frontend/src/App.tsx)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 3: User Story 1 (T002, T003)
3. **STOP and VALIDATE**: Quickstart §1 — only session list scrolls
4. Deploy/demo if ready

### Incremental Delivery

1. Add US1 → validate scroll behavior
2. Add US2 → validate dynamic titles and placeholder
3. Add US3 → validate session ID line and copy with toasts
4. Run full quickstart (T009)

### Optional Refactor

- If App.tsx grows, extract a shared `SessionSectionHeader` component (title + optional ID line + copy) and use it for both Logs & metrics and Reports; contracts in specs/008-scrollable-session-list-titles/contracts/ui-section-header-session-id.md.

---

## Notes

- [P] tasks: T006 marked [P] (can be same edit as T005)
- [Story] label links each task to US1/US2/US3 for traceability
- Each user story is independently testable via quickstart.md
- No backend or new routes; frontend-only in existing frontend/src
- Commit after each task or after each story checkpoint
