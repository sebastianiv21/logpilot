# Tasks: Merge Upload Logs with Logs & Metrics and Improve Layout

**Input**: Design documents from `specs/013-merge-upload-logs-layout/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` (api, lib, services)
- **Frontend**: `frontend/src/` (components, lib, services)
- **Tests**: `backend/tests/`, `frontend/tests/` as applicable

---

## Phase 1: Setup

**Purpose**: Ensure environment and branch for feature work.

- [x] T001 Ensure on branch `013-merge-upload-logs-layout` and backend/frontend dependencies installed (per plan.md)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend support for uploaded file name and upload time (updated_at) so US2 (file name and upload time in summary) and US3 (report gate using upload-summary) can be implemented.

**⚠️ CRITICAL**: No user story work that depends on API can complete until upload-summary returns `uploaded_file_name` and `updated_at`.

- [x] T002 [P] Add `uploaded_file_name` column (TEXT, nullable) to `session_upload_summary` schema in backend/app/lib/db.py (extend SCHEMA_SESSION_UPLOAD_SUMMARY and ensure migration/init adds column for existing DBs)
- [x] T003 Include `uploaded_file_name` in get_upload_summary return dict and in upsert_upload_summary parameters/INSERT in backend/app/lib/repositories.py
- [x] T004 Add `uploaded_file_name` and `updated_at` to UploadResultResponse; in get_upload_summary return both from repo; in upload_logs pass file.filename to upsert_upload_summary and include uploaded_file_name and updated_at in response in backend/app/api/upload.py

**Checkpoint**: GET/POST upload-summary return uploaded_file_name and updated_at; frontend can show file name, upload time, and use upload-summary for report gate.

---

## Phase 3: User Story 1 – Single Section for Upload and Logs/Metrics (Priority: P1) – MVP

**Goal**: One combined section titled "Logs & metrics" containing upload controls, latest upload summary, and the metrics link (no separate blocks).

**Independent Test**: Open app, select a session; confirm one section with heading "Logs & metrics" that includes upload (file picker, upload button, latest result) and the "Open in Grafana" control.

- [x] T005 [P] [US1] Merge upload and Logs & metrics into one section with single visible heading "Logs & metrics" containing UploadLogs and MetricsLink in frontend/src/App.tsx (remove duplicate "Logs & metrics" block; single section with one h2)

**Checkpoint**: User Story 1 is done; one merged "Logs & metrics" section visible.

---

## Phase 4: User Story 2 – Show Uploaded File Name and Loading State (Priority: P1)

**Goal**: Latest upload summary shows the uploaded file name and when the upload occurred when available; summary area shows a loading indicator while the upload-summary query is loading.

**Independent Test**: Upload a .zip file; summary shows its name (e.g. "my-logs.zip") and when the upload occurred (e.g. "2 hours ago" or date/time). After session switch, summary area shows loading then data with file name and upload time. New session shows loading then empty/neutral state.

- [ ] T006 [P] [US2] Add optional `uploaded_file_name` and `updated_at` (z.string().nullable() or z.string().optional()) to UploadResultSchema in frontend/src/lib/schemas.ts
- [ ] T007 [US2] Ensure getUploadSummary and uploadLogs response types and parsing include uploaded_file_name and updated_at in frontend/src/services/api.ts (implement after T006 so schema is available)
- [ ] T008 [US2] Display uploaded file name and when the upload occurred (e.g. date/time or relative time like "2 hours ago" from updated_at) in the latest upload summary block when present in frontend/src/components/UploadLogs.tsx
- [ ] T009 [US2] Show loading indicator (spinner or skeleton) in the upload summary area while upload-summary query is loading (isLoading/isFetching and no data); show empty/neutral state on 404 in frontend/src/components/UploadLogs.tsx

**Checkpoint**: User Story 2 is done; file name and upload time in summary and loading state work.

---

## Phase 5: User Story 3 – Improved Layout and Report Gate (Priority: P2)

**Goal**: Two-column grid (Logs & metrics | Reports), session title above; report generation unavailable until current session has at least one log upload (success/partial), with clear indication.

**Independent Test**: Home view shows two columns (Logs & metrics left, Reports right). With no upload for session, report generation is disabled with message (e.g. "Upload logs to generate reports"); after upload, reports become available. Layout stacks on narrow viewport.

- [ ] T010 [US3] Ensure home view uses two-column grid (one column "Logs & metrics", one column Reports; session title above) and collapses to stacked layout on narrow viewports in frontend/src/App.tsx
- [ ] T011 [US3] Gate report generation on session having upload: use upload-summary query (200 with status success/partial) or in-tab last upload result; disable the trigger to generate a new report (ReportGenerate) with clear message until upload exists; ReportList (viewing existing reports) remains visible in frontend/src/App.tsx and frontend/src/components/ReportGenerate.tsx

**Checkpoint**: User Story 3 is done; two-column layout and report gate work. Verify stacked layout on narrow viewport (FR-005).

---

## Phase 6: User Story 4 – Remove Helper Copy (Priority: P2)

**Goal**: Remove the sentence "Opens in a new tab; updates when you switch sessions." next to the metrics link; keep the button and its behavior.

**Independent Test**: Open view with "Open in Grafana"; confirm the phrase is not present; button still opens Grafana in a new tab.

- [ ] T012 [P] [US4] Remove the paragraph containing "Opens in a new tab; updates when you switch sessions." from frontend/src/components/MetricsLink.tsx (keep the button and onClick behavior)

**Checkpoint**: User Story 4 is done; copy removed, behavior unchanged.

---

## Phase 7: Polish & Cross-Cutting

**Purpose**: Validation and consistency.

- [ ] T013 Run quickstart.md validation (backend: upload returns uploaded_file_name and updated_at; GET upload-summary returns both; frontend: merged section, file name and upload time, loading state, two-column layout, report gate, no helper copy) and fix any gaps

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1. T002 → T003 → T004 (schema → repo → API). Blocks US2 (file name) and US3 (report gate data).
- **Phase 3 (US1)**: Can run after Phase 1; frontend-only merge, no backend dependency.
- **Phase 4 (US2)**: Depends on Phase 2 (API returns uploaded_file_name). Implement T006 before T007 (schema before API types); T008–T009 depend on T006/T007.
- **Phase 5 (US3)**: Depends on Phase 2 for upload-summary as source of "has upload". Layout (T010) can be done with US1; gate (T011) uses same upload-summary query as US2.
- **Phase 6 (US4)**: No dependency on other stories; can run in parallel with US2/US3.
- **Phase 7 (Polish)**: After all implementation tasks.

### User Story Dependencies

- **US1 (P1)**: Independent; merge UI only.
- **US2 (P1)**: Depends on Phase 2 (backend returns uploaded_file_name).
- **US3 (P2)**: Depends on Phase 2 for report gate; layout can follow US1.
- **US4 (P2)**: Independent.

### Parallel Opportunities

- T002 is parallelizable with other Phase 2 prep (only schema).
- T005 (US1), T006 (US2 schema), T012 (US4) are [P] within their phases.
- After Phase 2, US1 (T005), US2 (T006–T009), US3 (T010–T011), US4 (T012) can be parallelized by story.

---

## Parallel Example: After Foundational

```bash
# Frontend merge (US1) and copy removal (US4) can run in parallel:
Task T005: Merge section in frontend/src/App.tsx
Task T012: Remove helper copy in frontend/src/components/MetricsLink.tsx

# Then US2 and US3 (both use upload-summary):
Task T006–T009: File name + loading in UploadLogs
Task T010–T011: Two-column layout + report gate in App.tsx / ReportGenerate.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 + Foundational)

1. Phase 1: Setup  
2. Phase 2: Foundational (T002 → T003 → T004)  
3. Phase 3: US1 (T005) – merged "Logs & metrics" section  
4. **Validate**: One section with upload + metrics link, heading "Logs & metrics"

### Incremental Delivery

1. Setup + Foundational → API returns uploaded_file_name and updated_at  
2. US1 (merge) → Demo single section  
3. US2 (file name + upload time + loading) → Demo summary with filename, upload time, and loader  
4. US3 (layout + report gate) → Demo two columns and report gate  
5. US4 (remove copy) → Demo no helper text  
6. Polish (T013) → quickstart.md checklist

### Suggested MVP Scope

- **MVP**: Phase 1 + Phase 2 + Phase 3 (T001–T005) — backend file name support and single merged "Logs & metrics" section. Report gate and file name in UI can follow in next increment.
