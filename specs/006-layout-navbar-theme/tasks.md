# Tasks: App layout and navigation improvements

**Input**: Design documents from `/specs/006-layout-navbar-theme/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested in the feature specification; no test tasks included.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for components, hooks, App, main.tsx; `frontend/index.html` for FART script

---

## Phase 1: Setup (Theme-change and init)

**Purpose**: Initialize theme-change for React and optionally prevent flash of wrong theme on first load.

- [x] T001 Initialize theme-change in `frontend/src/main.tsx`: import `themeChange` from `theme-change` and call `themeChange(false)` once before `createRoot(...)` so it runs before first paint (per theme-change React docs, `themeChange(false)` is required for React). Do not use `useEffect` for the initial call—calling before mount avoids a flash of default theme.
- [x] T002 [P] Add optional FART prevention in `frontend/index.html`: inline script before the root div that, when `localStorage.getItem('theme')` is null, sets `document.documentElement.setAttribute('data-theme', ...)` from `window.matchMedia('(prefers-color-scheme: dark)').matches` (use `'dark'` or `'light'`); otherwise set from localStorage. Ensures initial theme is applied before React hydrates (see research.md).

**Checkpoint**: Theme-change is active; first load uses system preference or stored theme without visible flash.

---

## Phase 2: Foundational (Layout structure and sidebar visibility)

**Purpose**: Conditional sidebar so knowledge page has no sessions panel; top bar structure ready for LogPilot and theme switcher. Unblocks US1, US2, US4.

- [x] T003 In `frontend/src/components/AppLayout.tsx`, render the left sidebar (`<aside>` with Sessions heading, CreateSessionForm, SessionList) only when `location.pathname !== '/knowledge'`. When on `/knowledge`, do not render the sidebar at all so only the main content and top bar are visible. Preserve skip-to-main-content and main landmark.
- [x] T004 In `frontend/src/components/AppLayout.tsx`, add "LogPilot" to the top bar (navbar): left side, before the conditional "Back to home" link (or before the flex spacer on home). Ensure the top bar has a clear left region (LogPilot + optional back link) and right region (HeaderKbLink + slot for theme switcher). In `frontend/src/App.tsx`, remove the "LogPilot" main heading from the home page content (HomePage): change or remove the `<h1>LogPilot</h1>` so the primary page title is not "LogPilot" (branding lives in the top bar only). Confirm the left sidebar does not display "LogPilot" (it currently shows "Sessions"; no change needed if it does not).

**Checkpoint**: Sidebar hidden on `/knowledge`; LogPilot appears in the top bar on all pages; home page main content no longer uses LogPilot as the primary heading.

---

## Phase 3: User Story 1 — Theme switcher (Priority: P1) — MVP

**Goal**: User can change theme via a single control in the top bar (last item); theme persists across reloads; default is system preference (or light if unavailable).

**Independent Test**: Open app, use theme control to switch theme, verify UI updates; reload and confirm same theme; clear localStorage, reload, confirm default follows system (or light).

### Implementation for User Story 1

- [x] T005 [US1] Create a theme switcher component (e.g. `frontend/src/components/ThemeSwitcher.tsx`): sun/moon swap or toggle using theme-change (e.g. `data-toggle-theme="dark,light"` or `data-set-theme`). Use daisyUI swap or toggle markup if desired; ensure the control is accessible (aria-label, keyboard). Render it as the last item in the top bar in `frontend/src/components/AppLayout.tsx` (after HeaderKbLink).
- [x] T006 [US1] Implement default theme when no stored preference: on app init (in `frontend/src/main.tsx` or in ThemeSwitcher/AppLayout), when localStorage has no `theme` key, set `data-theme` from `window.matchMedia('(prefers-color-scheme: dark)').matches` (e.g. `'dark'` or `'light'`). If the media query is unavailable, default to `'light'`. Coordinate with T002 so the initial value is set before or at first paint.

**Checkpoint**: User Story 1 is independently testable; theme switcher works, persists, and defaults correctly.

---

## Phase 4: User Story 3 — Remove sidebar copy and instructional line (Priority: P3)

**Goal**: Home page does not show "Upload logs or switch session in the sidebar."; when no session is selected, one short instructional line is shown (e.g. "Select or create a session to get started.").

**Independent Test**: Open home page; confirm the exact phrase is not present; with no session selected, confirm the instructional line is visible.

### Implementation for User Story 3

- [x] T007 [US3] In `frontend/src/App.tsx` (HomePage), remove the exact phrase "Upload logs or switch session in the sidebar." from the paragraph under the main content heading. When `currentSessionId` is set, omit the subheading line entirely (no "sidebar" reference and no replacement phrase). When `currentSessionId` is not set, show exactly one short instructional line (e.g. "Select or create a session to get started.") per FR-004b.
- [x] T008 [US3] Verify the home page never displays "Upload logs or switch session in the sidebar." (text search or manual check) and that with no session selected the required instructional line is present (e.g. in `frontend/src/App.tsx`).

**Checkpoint**: User Story 3 is independently testable; copy meets FR-004 and FR-004b.

---

## Phase 5: Polish & validation

**Purpose**: Accessibility and quickstart validation.

- [x] T009 Run the validation steps in `specs/006-layout-navbar-theme/quickstart.md`: theme switcher (placement, toggle, persistence, default), sidebar hidden on knowledge page, copy and instructional line, LogPilot in top bar only, optional keyboard/accessibility checks.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies. Delivers theme-change init and optional FART prevention.
- **Phase 2 (Foundational)**: Depends on Phase 1 only if theme init is used before layout (no hard dependency). Delivers conditional sidebar (US2) and LogPilot in top bar + home heading removal (US4).
- **Phase 3 (US1)**: Depends on Phase 2 (top bar must exist and have a trailing slot). Delivers theme switcher and default theme.
- **Phase 4 (US3)**: No dependency on Phase 3; can be done in parallel with US1 after Phase 2. Delivers copy changes.
- **Phase 5**: After all implementation tasks.

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2 (top bar structure). Theme switcher last in navbar.
- **US2 (P2)**: Delivered in Phase 2 (T003). Sidebar hidden on `/knowledge`.
- **US3 (P3)**: Independent of US1/US2/US4; copy only in HomePage.
- **US4 (P4)**: Delivered in Phase 2 (T004). LogPilot in top bar; not in sidebar; not in home heading.

### Within Each User Story

- US1: T005 (theme component) then T006 (default theme); both touch theme behavior.
- US3: T007 implements copy; T008 is verification.

### Parallel Opportunities

- T001 and T002 can be done in parallel (main.tsx vs index.html).
- After Phase 2, T005–T006 (US1) and T007–T008 (US3) can be done in parallel (different files: AppLayout/ThemeSwitcher vs App.tsx).

---

## Parallel Example: After Phase 2

```bash
# User Story 1 (theme):
Task T005: "Create ThemeSwitcher and add last in top bar in frontend/src/components/AppLayout.tsx"
Task T006: "Default theme from system preference in main.tsx or ThemeSwitcher"

# User Story 3 (copy):
Task T007: "Remove sidebar phrase and set instructional line in frontend/src/App.tsx"
Task T008: "Verify copy in frontend/src/App.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 (T001, optionally T002).
2. Complete Phase 2 (T003, T004).
3. Complete Phase 3 (T005, T006).
4. **STOP and VALIDATE**: Theme switcher works, persists, defaults; sidebar hidden on knowledge; LogPilot in top bar; home has no LogPilot heading.

### Incremental Delivery

1. Phase 1 + 2 → Layout and branding ready (US2, US4 done).
2. Add Phase 3 (US1) → Theme switcher → Validate.
3. Add Phase 4 (US3) → Copy → Validate.
4. Phase 5 → Full quickstart validation.

### Parallel Team Strategy

- After Phase 2: One developer can do US1 (T005–T006), another US3 (T007–T008).

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to user story for traceability.
- Each user story is independently testable per spec.
- theme-change is already in `frontend/package.json`; no new dependency.
- Commit after each task or logical group; run quickstart after Phase 5.
