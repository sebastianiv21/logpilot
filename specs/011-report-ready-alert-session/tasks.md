# Tasks: Report-Ready Alert Shows Session Context and Go-to-Session Action

**Input**: Design documents from `specs/011-report-ready-alert-session/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/  
**Tests**: Not requested in spec; no test tasks included.  
**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for components, contexts, lib

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify frontend structure and dependencies per plan.

- [x] T001 Verify frontend structure and Sonner usage per plan in `frontend/` (no new project init; feature is frontend-only)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Report-to-open mechanism and provider order so ReportGenerationContext can pass openReport to the toast. Must complete before user story implementation.

- [x] T002 [P] Add ReportToOpenContext with state `reportToOpen: { sessionId: string, reportId: string } | null`, `openReport(sessionId, reportId)`, and `clearReportToOpen()` in `frontend/src/contexts/ReportToOpenContext.tsx`
- [x] T003 Add ReportToOpenProvider in `frontend/src/App.tsx` inside BrowserRouter (so it can use useNavigate); provider consumes SessionContext and implements openReport by setting currentSessionId, setting reportToOpen, and navigating to `/`
- [x] T004 Move ReportGenerationProvider from `frontend/src/main.tsx` into `frontend/src/App.tsx` so it sits inside ReportToOpenProvider; wrap Routes (and Toaster/ConnectionBanner) with ReportGenerationProvider in App
- [ ] T005 Update ReportGenerationContext to consume ReportToOpenContext and pass `openReport` into `notifyReportReady` when calling it (pass reportId and onViewReport) in `frontend/src/contexts/ReportGenerationContext.tsx`

**Checkpoint**: Foundation ready — report-to-open context and provider order in place; ReportGenerationContext can call notifyReportReady with openReport.

---

## Phase 3: User Story 1 - Report-Ready Alert Includes Session Identity (Priority: P1) — MVP

**Goal**: Every report-ready toast message includes the session identity (name or session ID) so users know which report is ready.

**Independent Test**: Generate a report (single or multiple sessions); when the toast appears, confirm the message includes session name or a short session identifier (never only "Report ready").

### Implementation for User Story 1

- [x] T006 [US1] Update `notifyReportReady` in `frontend/src/lib/reportReadyNotification.ts` to always include session identity in the message: use `getSessionLabel(sessionId)` for every toast (remove the `generatingCount > 1` branch so message is always e.g. "Report ready (Session name)" or "Report ready (abc12def)"); when the session name is very long, truncate for display and provide the full value via tooltip or title per FR-004
- [x] T007 [US1] Add `reportId: string` parameter to `notifyReportReady` in `frontend/src/lib/reportReadyNotification.ts` and add optional `onViewReport?: (sessionId: string, reportId: string) => void` for Phase 4; keep existing `getSessionLabel` fallback when session name cannot be resolved (per FR-001). Update the call in `frontend/src/contexts/ReportGenerationContext.tsx` to pass reportId and generatingCount to notifyReportReady, omitting onViewReport until Phase 4, so the app compiles after Phase 3

**Checkpoint**: User Story 1 complete — every report-ready toast shows session identity; notifyReportReady accepts reportId and optional onViewReport for US2.

---

## Phase 4: User Story 2 - One-Click Redirect to Session and Open Report (Priority: P2)

**Goal**: Toast includes a "View report" control that navigates to the session and opens that report so the user sees it immediately; control is keyboard-focusable and has an accessible name; unavailable session/report shows a clear message.

**Independent Test**: Trigger a report to become ready; click (or keyboard-activate) "View report" in the toast; confirm the app switches to that session and opens that report. If session/report is removed first, confirm a clear message and no broken view.

### Implementation for User Story 2

- [ ] T008 [US2] In `frontend/src/lib/reportReadyNotification.ts`, when `onViewReport` is provided call `toast.success(message, { action: { label: 'View report', onClick: () => onViewReport(sessionId, reportId) } })` and ensure the action control is keyboard-focusable and has an accessible name (e.g. Sonner action button or custom description with aria-label "View report") per FR-002 and FR-005
- [ ] T009 [US2] In `frontend/src/contexts/ReportGenerationContext.tsx`, add `openReport` from ReportToOpenContext as the fourth argument to the existing notifyReportReady call (sessionId, reportId, generatingCount already passed from T007)
- [ ] T010 [US2] In `frontend/src/components/ReportList.tsx`, consume reportToOpen from ReportToOpenContext; when `currentSessionId === reportToOpen.sessionId` and reports have loaded, if `reportToOpen.reportId` is in the reports list set selectedReport to that report (open modal) and call clearReportToOpen
- [ ] T011 [US2] In `frontend/src/components/ReportList.tsx`, when reportToOpen matches current session but reports failed to load or reportId is not in the list, show a clear toast (e.g. "Session or report no longer available") and call clearReportToOpen so the user gets a clear indication per FR-003 and SC-003

**Checkpoint**: User Story 2 complete — "View report" in toast opens session and report; keyboard/screen reader can activate it; unavailable case shows clear message.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Contract reference and quickstart validation.

- [ ] T012 [P] Update `frontend/src/lib/reportReadyNotification.ts` (or contract) comment to reference `specs/011-report-ready-alert-session/contracts/report-ready-notification.md`
- [ ] T013 Run quickstart validation from `specs/011-report-ready-alert-session/quickstart.md` (sections 1–5) and fix any regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — blocks US1 and US2
- **Phase 3 (US1)**: Depends on Phase 2 — notifyReportReady is called from ReportGenerationContext which now has openReport; message-only change can land before action
- **Phase 4 (US2)**: Depends on Phase 2 and Phase 3 — needs updated notifyReportReady signature and ReportToOpenContext/ReportList wiring
- **Phase 5 (Polish)**: Depends on Phase 4

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2 — message always includes session identity
- **User Story 2 (P2)**: After Phase 2 and Phase 3 — View report action and ReportList consumption of reportToOpen

### Within Each User Story

- US1: T006 then T007 (T007 updates both reportReadyNotification.ts and ReportGenerationContext call so the app compiles after Phase 3; T009 adds openReport in Phase 4)
- US2: T008–T011; T009 (add openReport to existing call) and T010–T011 (ReportList) can be done in either order after T008

### Parallel Opportunities

- T002 is [P] within Phase 2 (new file)
- T012 is [P] in Phase 5
- After Phase 2, T006–T007 (US1) can be done then T008–T011 (US2); no parallel across stories for same files

---

## Parallel Example: Phase 2

```text
T002: Create ReportToOpenContext in frontend/src/contexts/ReportToOpenContext.tsx
(Then T003–T005 sequentially: App.tsx provider + move ReportGenerationProvider, then ReportGenerationContext update)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup)
2. Complete Phase 2 (Foundational)
3. Complete Phase 3 (US1)
4. **STOP and VALIDATE**: Confirm every report-ready toast shows session identity (quickstart §1)
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → report-to-open mechanism ready
2. Add US1 → validate session identity in toast (MVP)
3. Add US2 → validate "View report" and accessibility
4. Polish → contract ref and quickstart

### Notes

- [P] tasks = different files or no dependencies
- [Story] label maps task to user story for traceability
- Each user story is independently testable per quickstart
- Commit after each task or logical group
- No test tasks; spec did not request tests
