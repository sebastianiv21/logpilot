# Implementation Plan: Merge Upload Logs with Logs & Metrics and Improve Layout

**Branch**: `013-merge-upload-logs-layout` | **Date**: 2026-03-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/013-merge-upload-logs-layout/spec.md`

## Summary

Merge the upload-logs block and the "Logs & metrics" block into a single section titled "Logs & metrics" (upload controls, latest upload summary with uploaded file name, and metrics link). Use a two-column home layout (Logs & metrics | Reports), remove the helper copy "Opens in a new tab; updates when you switch sessions.", show a loading indicator while the upload summary loads, and gate report generation on the current session having at least one log upload. Backend stores and returns the uploaded file name with the upload summary so it is available after refresh or session switch.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: FastAPI, React 18.x, Vite, Tailwind CSS, DaisyUI, TanStack Query  
**Storage**: SQLite (sessions, session_upload_summary, session_log_extent); add `uploaded_file_name` to session_upload_summary  
**Testing**: pytest (backend), Vitest/React Testing Library (frontend)  
**Target Platform**: Web (browser); backend runs locally (e.g. Docker Compose)  
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: Interactive upload-to-summary and layout; no new NFRs for this feature  
**Constraints**: Local-first; no mandatory cloud; scope within PRD  
**Scale/Scope**: Single user / single deployment; existing session and upload volume

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: No change; design remains local deployment; upload and summary stay server-side under user control.
- **Observability-First**: Logs and metrics flows unchanged; merge is UI-only; upload summary still reflects log ingestion.
- **Evidence-Backed AI**: No change; report generation is gated on upload (ensures data exists before AI report).
- **User Stories**: Spec has independently testable user stories (merge section, file name, layout, remove copy, loading state, report gate) with acceptance criteria.
- **Simplicity**: Scope bounded to merge, file name in summary, layout, copy removal, loading state, and report gate; no new services or enterprise features.

## Project Structure

### Documentation (this feature)

```text
specs/013-merge-upload-logs-layout/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contract)
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/  (or app/)
│   ├── api/upload.py      # Add uploaded_file_name to response and storage
│   ├── lib/db.py         # session_upload_summary schema + uploaded_file_name column
│   ├── lib/repositories.py  # get_upload_summary / upsert_upload_summary include file name
│   └── services/upload.py   # UploadResult unchanged; API layer passes file.filename to repository
└── tests/

frontend/
├── src/
│   ├── App.tsx           # Two-column layout; single "Logs & metrics" section (upload + MetricsLink)
│   ├── components/
│   │   ├── UploadLogs.tsx      # Show file name from API; loading state in summary area
│   │   ├── MetricsLink.tsx      # Remove helper copy
│   │   └── ReportGenerate.tsx   # Disable/hide until session has upload (from upload-summary or context)
│   ├── lib/schemas.ts    # UploadResult + uploaded_file_name (optional string)
│   └── services/api.ts   # Types and getUploadSummary/uploadLogs
└── tests/
```

**Structure Decision**: Existing backend + frontend layout; changes are additive (DB column, API field, UI merge and gate).

## Complexity Tracking

> No constitution violations. Table left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| —         | —          | —                                    |
