# Tasks: Session External Link Button in Main Content

**Input**: Design documents from `specs/012-session-external-link-button/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included.

**Organization**: Single user story (P1); tasks grouped by phase. Foundation is existing frontend and session data.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = User Story 1 (Open Session External Link from Main Content)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for components and app code

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm existing stack and session shape; no new dependencies.

- [x] T001 [P] Verify Session type and sessions API expose `external_link` in `frontend/src/lib/schemas.ts` and `frontend/src/services/api.ts` (confirm only; no changes required)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No new infrastructure; existing session data and HomePage structure suffice.

**Checkpoint**: Foundation ready — User Story 1 implementation can begin.

*(No tasks; current session and title block in `App.tsx` already provide what is needed.)*

---

## Phase 3: User Story 1 - Open Session External Link from Main Content (Priority: P1) MVP

**Goal**: User always sees an "External link" control (icon + text) next to the session title. When the session has a non-empty external link, the control is enabled and activating it opens that URL in a new tab. When the session has no external link, the control is disabled and shows a tooltip (e.g. "No external link provided").

**Independent Test**: Create or select a session with an external link set → control is enabled next to title; click it → link opens in new tab and app stays in current tab. Select a session without external link → control is visible but disabled with tooltip. Keyboard/screen reader can focus the control; when enabled, activation navigates; when disabled, tooltip/aria explains no link provided.

### Implementation for User Story 1

- [x] T002 [US1] Add external link control next to session title in `frontend/src/App.tsx`: always show the control (icon + "External link" text) to the right of the title. When `currentSession.external_link` is non-empty after trim, render an `<a>` with `href={trimmedExternalLink}`, `target="_blank"`, `rel="noopener noreferrer"`, `aria-label="Open session's external link"`. When no external link (null/empty/whitespace), render the control in a disabled state (e.g. `<span>` or disabled button/link with `aria-disabled="true"` and pointer-events none, or non-clickable anchor) with a tooltip "No external link provided" (e.g. `title` or DaisyUI tooltip) and `aria-label="External link — no link provided"`. Use `ExternalLink` icon from lucide-react and visible text "External link"; when disabled use muted styling. Place control in the existing title block (e.g. wrap title and control in a flex container) per `specs/012-session-external-link-button/contracts/main-content-external-link.md`

**Checkpoint**: User Story 1 is complete and independently testable via quickstart.md.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validation and optional cleanup.

- [ ] T003 Run `specs/012-session-external-link-button/quickstart.md` validation (manual steps 1–5) to confirm all acceptance scenarios and edge cases (validates SC-001–SC-004)
- [ ] T004 [P] (Optional) Extract session title row (title + optional external link + session ID) into a presentational component under `frontend/src/components/` if desired for clarity; keep behavior unchanged per plan.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately.
- **Phase 2 (Foundational)**: No tasks — no blocking work.
- **Phase 3 (US1)**: Depends on Phase 1 confirmation; implement in `App.tsx`.
- **Phase 4 (Polish)**: T003 after T002; T004 optional and parallel.

### User Story Dependencies

- **User Story 1 (P1)**: Only story; no dependencies on other stories. Can start after T001 (or in parallel if schema/API already known).

### Within User Story 1

- T002 is the single implementation task; no internal ordering.

### Parallel Opportunities

- T001 is [P] (read-only verification).
- T004 is [P] and optional (refactor after T002).
- No parallel work within US1 (one task).

---

## Parallel Example: User Story 1

```bash
# Single implementation task; no parallel within US1.
# After T001 (or in parallel): run T002 to add the control in frontend/src/App.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: T001 (verify schema/API).
2. Phase 2: No tasks.
3. Complete Phase 3: T002 (add external link control in App.tsx).
4. **STOP and VALIDATE**: Run quickstart.md steps 1–4.
5. Phase 4: T003 (full quickstart validation); optionally T004 (refactor).

### Incremental Delivery

- This feature has one user story; delivering T002 completes the MVP. T003 validates; T004 is optional polish.

---

## Notes

- [P] tasks = different files or verification only; no dependencies.
- [US1] maps to the single P1 user story.
- No test tasks; spec does not request automated tests.
- Commit after T002 and again after T003.
- Control must be keyboard-focusable (native `<a>` is by default) and have an accessible name per FR-005.
