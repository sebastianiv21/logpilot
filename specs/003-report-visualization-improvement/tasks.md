# Tasks: Report Visualization Improvement

**Input**: Design documents from `/specs/003-report-visualization-improvement/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No test tasks added; spec does not explicitly request TDD or automated tests. Manual validation via quickstart.md is in Polish phase.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure dependencies and project layout support report visualization work.

- [ ] T001 Verify or add `react-markdown` dependency in `frontend/package.json` (used by ReportView; add if missing per research §6)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Content format that all export and display paths depend on. No user story work that relies on report content can succeed until the agent outputs the correct format.

**⚠️ CRITICAL**: Agent prompt update blocks correct numbered list in browser, Markdown export, and PDF export.

- [ ] T002 Update system prompt in `backend/app/services/agent.py` to require that the "Next troubleshooting steps" section be output as a Markdown numbered list (e.g. `1. First step`, `2. Second step`); keep all other report rules unchanged

**Checkpoint**: New reports will contain numbered troubleshooting steps in raw content; frontend and export can now rely on it.

---

## Phase 3: User Story 1 - Readable Report in Browser (Priority: P1) 🎯 MVP

**Goal**: In-app report view has clear hierarchy, readable typography, list and code styling, long-line wrap, and baseline accessibility so users can scan and read without confusion.

**Independent Test**: Open any generated report in the browser; confirm section headings are distinct, lists and code are clearly formatted, long lines wrap, and layout holds at 200% zoom.

### Implementation for User Story 1

- [ ] T003 [US1] Improve report content styling in `frontend/src/components/ReportView.tsx`: clear heading hierarchy (`[&_h1]`, `[&_h2]`, `[&_h3]`), list spacing and indentation, ensure `<ol>` uses `list-decimal` and `<ul>` uses `list-disc`, code/pre monospace and background, add `break-words` or `overflow-wrap: break-word` on report content container for long lines (FR-001, FR-002, FR-006, FR-007); preserve semantic markup for baseline accessibility and readable contrast (FR-008)

**Checkpoint**: User Story 1 is complete; report view is readable and accessible in the browser.

---

## Phase 4: User Story 2 - Troubleshooting Steps as Numbered List (Priority: P1)

**Goal**: The "Next troubleshooting steps" section is rendered and exported as a numbered list (1., 2., 3., …) in the browser, Markdown export, and PDF export.

**Independent Test**: Generate a report, view in browser (numbered list), export as Markdown (numbered in file), export as PDF (numbered in PDF).

### Implementation for User Story 2

- [ ] T004 [US2] Update PDF export in `backend/app/services/export.py`: parse HTML from Markdown to distinguish `<ol>` vs `<ul>`; for each `<li>` record whether it belongs to an ordered list and its 1-based index; render `<ol>` items as `"1. text"`, `"2. text"`, etc., and `<ul>` items as `"• text"` in ReportLab flowables (FR-003, FR-005)
- [ ] T005 [US2] Optional: Add a small normalizer in `backend/app/services/export.py` that ensures the "Next troubleshooting steps" section uses Markdown numbered list syntax (`1.`, `2.`, …) and call it from `export_markdown` before returning, as robustness fallback when agent output is bullet list there

**Checkpoint**: User Story 2 is complete; troubleshooting steps are numbered in browser (from T002 + T003), Markdown export, and PDF export.

---

## Phase 5: User Story 3 - Professional Exported Markdown (Priority: P2)

**Goal**: Exported Markdown file is well-formed so headings, lists (including numbered troubleshooting steps), code blocks, and paragraphs render correctly in common Markdown viewers.

**Independent Test**: Export a report as Markdown; open in GitHub preview or a standard editor; confirm structure and numbered troubleshooting list render correctly.

### Implementation for User Story 3

- [ ] T006 [US3] Ensure `export_markdown` in `backend/app/services/export.py` returns well-formed content: passthrough of report content; if normalizer from T005 is implemented, apply it before returning so the downloaded `.md` has numbered troubleshooting steps (FR-004)

**Checkpoint**: User Story 3 is complete; Markdown export is professional and valid.

---

## Phase 6: User Story 4 - Professional Exported PDF (Priority: P2)

**Goal**: Exported PDF has clear section hierarchy, readable body text and spacing, numbered troubleshooting list, and no cut-off or overlapping text at 100% zoom or when printed.

**Independent Test**: Export a report as PDF; open in a standard reader; confirm hierarchy, numbered list, and readability; print or zoom to confirm no layout break.

### Implementation for User Story 4

- [ ] T007 [US4] Improve PDF layout and readability in `backend/app/services/export.py`: consistent spacing between sections, margins and line length suitable for print (A4/Letter), and pagination that preserves list numbering across pages for long reports (FR-005, SC-004)

**Checkpoint**: User Stories 1–4 are complete; report visualization meets spec in browser and both exports.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Export error handling and validation that affect multiple flows.

- [ ] T008 [P] Harden export failure handling in `frontend/src/components/ReportView.tsx`: ensure toast shows a clear, user-friendly error message (e.g. "Export failed. Try again.") when export fails; use backend `detail` when it is a clear message, otherwise generic text. If the export API client in `frontend/src/services/api.ts` surfaces raw errors, ensure ReportView (or the client) maps them to a user-friendly message (FR-009)
- [ ] T009 Run validation steps from `specs/003-report-visualization-improvement/quickstart.md`: generate report, validate in-browser view, Markdown export, PDF export, and export failure message

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 — T002 blocks correct content for US2, US3, US4.
- **Phase 3 (US1)**: Depends on Phase 1 — frontend styling only; can start after T001.
- **Phase 4 (US2)**: Depends on Phase 2 and Phase 3 — T004 (PDF ol/ul) and optional T005; browser numbering comes from T002 + T003.
- **Phase 5 (US3)**: Depends on Phase 2; T006 may depend on T005 if normalizer is implemented.
- **Phase 6 (US4)**: Depends on T004 and T007 — PDF list numbering and layout.
- **Phase 7 (Polish)**: Depends on all story phases — T008 any time after ReportView exists; T009 after all implementation.

### User Story Dependencies

- **User Story 1 (P1)**: After T001; no dependency on other stories. Delivers readable in-browser report.
- **User Story 2 (P1)**: After T002 (content) and T003 (frontend lists); T004 and optional T005 deliver PDF and MD numbering.
- **User Story 3 (P2)**: After T002; T006 ensures Markdown export quality (and normalizer if present).
- **User Story 4 (P2)**: After T004 (PDF lists) and T007 (PDF layout).

### Within Each User Story

- US1: Single implementation task (T003).
- US2: PDF export (T004) then optional normalizer (T005).
- US3: Markdown export (T006).
- US4: PDF layout (T007).

### Parallel Opportunities

- T003 (US1) and T002 (Foundational) can be done in parallel by different people; T002 unblocks US2/US3/US4.
- T008 (Polish) can run in parallel with any later task (different file).
- After Phase 2, US1 (T003), US2 (T004, T005), US3 (T006), and US4 (T007) can be sequenced or partially parallelized (e.g. T004 and T007 both touch `export.py` — order T004 then T007).

---

## Parallel Example: After Foundational

```text
# Backend developer:
T004 Update PDF export in backend/app/services/export.py (ol/ul)
T005 Optional normalizer in backend/app/services/export.py
T006 Ensure export_markdown in backend/app/services/export.py
T007 Improve PDF layout in backend/app/services/export.py

# Frontend developer (after T001):
T003 Improve ReportView in frontend/src/components/ReportView.tsx
T008 Harden export error message in frontend/src/components/ReportView.tsx
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Phase 1: T001 (verify/add react-markdown).
2. Phase 2: T002 (agent prompt — numbered troubleshooting steps).
3. Phase 3: T003 (ReportView styling and a11y) → validate in-browser report (US1).
4. Phase 4: T004 (PDF ol/ul), optionally T005 (normalizer) → validate browser + MD + PDF numbering (US2).
5. **Stop and validate**: Quickstart §2–4; then deploy/demo if ready.

### Incremental Delivery

1. Setup + Foundational → content format ready.
2. Add US1 (T003) → test in-browser independently.
3. Add US2 (T004, T005) → test numbered list in all three outputs.
4. Add US3 (T006) → test Markdown export quality.
5. Add US4 (T007) → test PDF layout and print.
6. Polish (T008, T009) → export errors and full quickstart validation.

### Parallel Team Strategy

- One developer: T001 → T002 → T003 → T004 → T005/T006 → T007 → T008 → T009.
- Two developers: After T002, Dev A does T003 + T008 (frontend); Dev B does T004 → T006 → T007 (backend). Then T009 together.

---

## Notes

- [P] tasks can run in parallel where files and dependencies allow.
- [USn] labels map tasks to user stories for traceability.
- Each user story has an independent test criterion in the spec and quickstart.
- Commit after each task or logical group.
- T005 is optional; skip if prompt-only approach is sufficient for your environment.
