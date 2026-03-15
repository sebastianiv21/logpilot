# Tasks: Upload State Scoped Per Session and Persistent Across Refresh

**Input**: Design documents from `/specs/010-upload-session-state-fix/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm structure and dependencies; no new packages per plan.

- [ ] T001 Verify backend and frontend structure per plan.md (backend/app with api/, lib/, services/; frontend/src with components/, contexts/, services/; no new dependencies required)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend storage and GET upload-summary endpoint required for US2 (state after refresh). US1 (session-scoped display) can be done without this; US2 cannot.

**⚠️ CRITICAL**: Phase 4 (US2) depends on this phase.

- [ ] T002 Add `session_upload_summary` table in backend/app/lib/db.py (session_id PK/FK, status, files_processed, files_skipped, lines_parsed, lines_rejected, error, updated_at per data-model.md)
- [ ] T003 Add get_upload_summary(session_id) and upsert_upload_summary(session_id, result) to SessionRepository in backend/app/lib/repositories.py
- [ ] T004 In backend/app/api/upload.py after successful POST upload response, call repository upsert_upload_summary so last result is persisted
- [ ] T005 Add GET /sessions/{session_id}/upload-summary endpoint (e.g. in backend/app/api/upload.py) returning 200 with UploadResult shape or 404 per contracts/api-upload-summary.md

**Checkpoint**: Backend persists last upload result and exposes GET upload-summary; US2 frontend can refetch.

---

## Phase 3: User Story 1 - Upload Result Shown Only for Current Session (Priority: P1) 🎯 MVP

**Goal**: Upload summary shows only for the currently selected session; switching sessions shows that session’s result or empty—no cross-session display.

**Independent Test**: Upload to session A, switch to session B → summary shows B’s result or empty; switch back to A → A’s result shown again.

### Implementation for User Story 1

- [ ] T006 [P] [US1] Add lastUploadResultBySessionId storage (e.g. Map or Record) and setLastUploadResult(sessionId, result) in frontend/src/contexts/SessionContext.tsx for result keyed by session id
- [ ] T007 [US1] In frontend/src/components/UploadLogs.tsx, display upload result only when result.session_id === currentSessionId; when session changes show result for new session from context (lastUploadResultBySessionId) or empty
- [ ] T008 [US1] On upload success in frontend/src/components/UploadLogs.tsx, store result in context via setLastUploadResult(variables.sessionId, data) and call markSessionHasLogs(variables.sessionId)
- [ ] T009 [US1] In frontend/src/components/UploadLogs.tsx ensure upload in progress is tied to originating session; on completion show result only when that session is selected (no cross-session display)

**Checkpoint**: User Story 1 is testable: switch sessions and confirm only current session’s result (or empty) is shown.

---

## Phase 4: User Story 2 - Upload and "Has Logs" State Survives Page Refresh (Priority: P2)

**Goal**: After refresh, app knows which sessions have logs and shows last upload summary for selected session; loading indicator, error + retry (selected session only), success toast after retry.

**Independent Test**: Upload to a session, refresh page, select same session → loading then last upload summary and “has logs” without re-upload; simulate error → error + retry → success toast.

### Implementation for User Story 2

- [ ] T010 Add getUploadSummary(sessionId) in frontend/src/services/api.ts calling GET /sessions/{session_id}/upload-summary (return UploadResult or null on 404; use existing UploadResultSchema)
- [ ] T011 [US2] Add useQuery for upload summary keyed by currentSessionId in frontend/src/components/UploadLogs.tsx with query key ['uploadSummary', sessionId]; enabled when sessionId is set; handle loading and error
- [ ] T012 [US2] On app load and when currentSessionId changes, use upload-summary query for current session; on 200 call markSessionHasLogs(sessionId) and use query data for display; on 404 show empty; ensure displayed result for current session comes from query when available (merge with in-context result from US1)
- [ ] T013 [US2] Show loading indicator (e.g. spinner or skeleton) in frontend/src/components/UploadLogs.tsx while upload-summary is loading for current session (FR-006)
- [ ] T014 [US2] On upload-summary fetch error in frontend show error message and retry control (e.g. button); refetch only for current session (FR-007)
- [ ] T015 [US2] After successful retry show loaded state and brief success message (e.g. toast "Loaded") in frontend (FR-007)
- [ ] T016 [P] [US2] Optional: Add has_logs to GET /sessions response in backend/app/api/sessions.py and extend frontend session list types in frontend/src/services/api.ts and display in frontend/src/components/SessionList.tsx

**Checkpoint**: User Story 2 is testable: refresh and select session → loading then summary; error path → retry → success toast.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation and docs.

- [ ] T017 Run quickstart.md validation from specs/010-upload-session-state-fix/quickstart.md (manual or script)
- [ ] T018 [P] Update specs/010-upload-session-state-fix/contracts/api-upload-summary.md if implementation diverges from contract

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies — start immediately
- **Phase 2**: Depends on Phase 1 — blocks Phase 4 (US2)
- **Phase 3 (US1)**: Depends on Phase 1 only — can run in parallel with Phase 2 or after
- **Phase 4 (US2)**: Depends on Phase 2 and Phase 3 (needs GET upload-summary and session-scoped display)
- **Phase 5**: Depends on Phase 3 and Phase 4 complete

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 1; no dependency on Phase 2. Delivers session-scoped display and in-memory result keyed by session.
- **User Story 2 (P2)**: After Phase 2 (backend) and Phase 3 (display scoping). Adds refetch on load, loading/error/retry, success toast.

### Within Each User Story

- US1: T006 (context) before T007–T009 (display and store)
- US2: T010 (api) before T011; T011 before T012–T015

### Parallel Opportunities

- Phase 2: T002 → T003 → then T004 and T005 can run in parallel (different concerns: persist in upload handler vs new GET endpoint)
- Phase 3: T006 is standalone; T007, T008, T009 are sequential in UploadLogs
- Phase 4: T010 then T011; T013, T014, T015 can be done together in UploadLogs; T016 optional and [P]
- Phase 5: T017 and T018 [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# After T006 (context storage):
# T007 (display logic) and T008 (store on success) both touch UploadLogs.tsx; do T007 then T008 then T009.
```

---

## Parallel Example: User Story 2

```bash
# After T011 (useQuery):
# T012 (wire load + hydrate), T013 (loading UI), T014 (error+retry), T015 (success toast) can be implemented together in UploadLogs.
# T016 (has_logs on list) is optional and independent.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup)
2. Complete Phase 3 (US1): session-scoped display and in-memory result keyed by session
3. **STOP and VALIDATE**: Switch sessions and confirm no cross-session result
4. Demo: upload to A, switch to B (empty or B’s), switch back to A (A’s result)

### Incremental Delivery

1. Phase 1 + Phase 2 → backend ready for refetch
2. Phase 3 (US1) → test session-scoped display (MVP)
3. Phase 4 (US2) → test refresh, loading, error+retry, success toast
4. Phase 5 → quickstart validation and contract update

### Suggested MVP Scope

- **MVP**: Phase 1 + Phase 3 (User Story 1). Fixes cross-session display without backend changes. Optionally add Phase 2 so US2 can be added next.

---

## Notes

- [P] = different files or optional; no dependency on same-phase incomplete tasks
- [US1]/[US2] maps task to user story for traceability
- No test tasks: spec does not request explicit tests
- Commit after each task or logical group; validate at checkpoints
