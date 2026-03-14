# Tasks: Log Investigation Platform MVP

**Input**: Design documents from `/specs/001-log-investigation-mvp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/` (per plan.md). Run dev server: `cd backend && uv run fastapi dev app/main.py`
- **Infrastructure**: `docker-compose.yaml` at repo root, `docker/` for Grafana provisioning

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md: backend/app/models, backend/app/services, backend/app/api, backend/app/lib, backend/tests/contract, backend/tests/integration, backend/tests/unit
- [x] T002 Initialize Python 3.11+ project in backend/ with pyproject.toml (or requirements.txt) including FastAPI, httpx, uvicorn, openai, qdrant-client
- [x] T003 [P] Add docker-compose.yaml at repo root with services: Loki, Prometheus, Grafana, Qdrant (ports per quickstart.md)
- [x] T004 Add backend service to docker-compose.yaml (build from backend/, env from config, depends_on: Loki, Prometheus, Grafana, Qdrant; expose API port e.g. 8000) so full stack runs with one orchestration (FR-013)
- [x] T005 [P] Configure ruff and pytest in backend/ (pyproject.toml or setup.cfg)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create SQLite schema and initialization for sessions and reports tables in backend/app/lib/db.py (or backend/app/models/db.py)
- [x] T007 Implement application config from environment (LOKI_URL, PROMETHEUS_URL, QDRANT_URL, LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, DATA_DIR) in backend/app/lib/config.py
- [x] T008 [P] Create Session model (id, name, external_link, created_at, updated_at) in backend/app/models/session.py
- [x] T009 [P] Create Report model (id, session_id, content, created_at) in backend/app/models/report.py
- [x] T010 Implement Session repository (CRUD) and Report repository (create, list by session, get by id) in backend/app/lib/repositories.py (or backend/app/services/session_repo.py and report_repo.py)
- [x] T011 Setup FastAPI app with router mounting and global exception handler returning structured detail (400/404/413/422) in backend/app/api/app.py
- [x] T012 Implement Loki push client (POST /loki/api/v1/push with labels and nanosecond timestamps) in backend/app/lib/loki_client.py
- [x] T013 [P] Add contract test for sessions API (list, create, get, update) and upload response schema per specs/001-log-investigation-mvp/contracts/api.md in backend/tests/contract/test_api_sessions.py

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — Ingest and Query Logs (Priority: P1) — MVP

**Goal**: Upload compressed log archives, parse and normalize log lines, store in Loki with session-scoped labels; sessions CRUD and optional log query API. Session scoping in MVP is path-only (session_id in URL); no "current session" header or POST required (see contracts/api.md).

**Independent Test**: Upload a valid compressed log archive, verify parsing summary (files_processed, lines_parsed, lines_rejected), then query by label and time range to retrieve log lines.

- [x] T014 [US1] Implement safe zip extraction with path traversal validation (pathlib.Path resolve, is_relative_to) in backend/app/lib/archive.py
- [x] T015 [US1] Implement log file pattern filter (.log, .csv, .json; optional .log.*, stdout, stderr) and archive size checks (100 MB compressed, 500 MB uncompressed) in backend/app/services/upload.py
- [x] T016 [US1] Implement log line parser: JSON parse first, then regex patterns with named groups (timestamp, level, message); normalized schema; preserve raw_message; report parsed/rejected counts in backend/app/services/log_parser.py
- [x] T017 [US1] Implement service/environment label derivation from archive path (path-based convention e.g. logs/<service>/<env>; fallback to single upload-scoped label) in backend/app/services/labels.py
- [x] T018 [US1] Implement upload pipeline: extract → filter → parse → normalize → push to Loki with session_id and labels; return upload result (status, files_processed, files_skipped, lines_parsed, lines_rejected, session_id, error) in backend/app/services/upload.py
- [x] T019 [US1] Implement session CRUD API: GET /sessions, POST /sessions, GET /sessions/{session_id}, PATCH /sessions/{session_id} in backend/app/api/sessions.py
- [x] T020 [US1] Add POST /sessions/{session_id}/logs/upload endpoint (multipart file; 413/400 on size or validation; 404 if session not found) in backend/app/api/upload.py
- [x] T021 [US1] Add POST /sessions/{session_id}/logs/query endpoint (time range, label filters; return log records with raw_message) in backend/app/api/logs.py

**Checkpoint**: User Story 1 complete — upload and query logs by session

---

## Phase 4: User Story 2 — View Derived Metrics and Dashboards (Priority: P2)

**Goal**: Derive metrics from ingested logs (errors_total, requests_total, error_rate, response_time when present), expose to Prometheus, provision at least one default Grafana dashboard.

**Independent Test**: Ingest logs with relevant fields; verify derived metrics are queryable and at least one dashboard shows error rate, request volume, error distribution, log volume.

- [ ] T022 [US2] Implement metrics derivation from log events (errors_total, requests_total, error_rate, response_time distribution when latency present) in backend/app/services/metrics.py
- [ ] T023 [US2] Expose or push derived metrics to Prometheus with session-scoped labels in backend/app/lib/prometheus_client.py
- [ ] T024 [US2] Add Grafana provisioning config for at least one default dashboard (error rate, request volume, error distribution, log volume) in docker/grafana/provisioning/dashboards/ or equivalent
- [ ] T025 [US2] Ensure dashboard panels and datasource are scoped to session (or document session selector usage) in dashboard JSON

**Checkpoint**: User Story 2 complete — metrics and dashboard available

---

## Phase 5: User Story 3 — Search Documentation and Repository Context (Priority: P3)

**Goal**: Ingest documentation and repo content, chunk and embed, store in Qdrant with source metadata; repeatable ingestion and semantic search API.

**Independent Test**: Ingest markdown/text and source files; run semantic search; verify chunks returned with source_path and metadata.

- [ ] T026 [US3] Implement chunking and embedding for docs/repo content (markdown, text, source) in backend/app/services/knowledge.py
- [ ] T027 [US3] Implement Qdrant client: store chunks with content, embedding, source_path, document_type, metadata in backend/app/lib/qdrant_client.py
- [ ] T028 [US3] Add POST /knowledge/ingest endpoint (sources from body or config; repeatable) in backend/app/api/knowledge.py
- [ ] T029 [US3] Add POST /knowledge/search endpoint (query, limit; return chunks with content, source_path, metadata) in backend/app/api/knowledge.py

**Checkpoint**: User Story 3 complete — knowledge base ingest and search

---

## Phase 6: User Story 4 — AI-Assisted Incident Investigation and Structured Report (Priority: P4)

**Goal**: AI agent with approved tools; user-triggered report generation; structured report stored per session; export as Markdown or PDF; report history.

**Independent Test**: After logs, metrics, and knowledge are available, ask an incident question; verify agent uses tools and report has required sections; export report as Markdown and PDF.

- [ ] T030 [US4] Implement configurable LLM client (OpenAI base_url + api_key from config) in backend/app/lib/llm_client.py
- [ ] T031 [US4] Implement agent tools: query_logs, query_metrics, search_docs, search_repo with input validation and session/time scope per specs/001-log-investigation-mvp/contracts/agent-tools.md in backend/app/services/agent_tools.py
- [ ] T032 [US4] Implement generate_incident_report and structured report schema (Incident Summary, Possible Root Cause, Supporting Evidence, Recommended Fix, next steps) in backend/app/services/agent.py
- [ ] T033 [US4] Implement agent orchestration (question → tool calls → report; prompt injection resistance; store report in session) in backend/app/services/agent.py
- [ ] T034 [US4] Add POST /sessions/{session_id}/reports/generate (body: question; store report; return report id and optional content) in backend/app/api/reports.py
- [ ] T035 [US4] Add GET /sessions/{session_id}/reports and GET /sessions/{session_id}/reports/{report_id} in backend/app/api/reports.py
- [ ] T036 [US4] Implement report export (Markdown: return content; PDF: weasyprint or reportlab) in backend/app/services/export.py
- [ ] T037 [US4] Add GET /sessions/{session_id}/reports/{report_id}/export?format=markdown|pdf in backend/app/api/reports.py

**Checkpoint**: User Story 4 complete — end-to-end investigation and export

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation

- [ ] T038 [P] Update README with setup, env vars, and link to quickstart in specs/001-log-investigation-mvp/quickstart.md
- [ ] T039 Run full quickstart.md flow (compose up, create session, upload, Grafana, ingest, generate report, export) and fix gaps

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 — no other story dependency
- **Phase 4 (US2)**: Depends on Phase 2 and US1 (metrics from logs)
- **Phase 5 (US3)**: Depends on Phase 2 — no US1/US2 dependency
- **Phase 6 (US4)**: Depends on Phase 2, US1, US2, US3 (agent uses logs, metrics, knowledge)
- **Phase 7 (Polish)**: Depends on at least US1; full validation after US4

### User Story Dependencies

- **US1 (P1)**: After Foundational only — MVP scope
- **US2 (P2)**: After Foundational + US1 (metrics derived from logs)
- **US3 (P3)**: After Foundational only — can parallel with US1/US2
- **US4 (P4)**: After US1, US2, US3 — needs logs, metrics, knowledge

### Parallel Opportunities

- Phase 1: T003 and T005 can run in parallel; T004 (backend in compose) after T003
- Phase 2: T008, T009, T013 can run in parallel after T006–T007
- Phase 5: T026/T027 can overlap with T028/T029 (same story, order within story)
- Phase 7: T038 can run in parallel with other polish

---

## Parallel Example: User Story 1

```text
# After T014–T017, these can proceed in order; T019 and T020/T021 touch different routers:
# T019 sessions.py, T020 upload.py, T021 logs.py — can be developed in parallel after T018
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Upload archive, verify parsing summary, query logs by label/time
5. Demo log ingestion and query

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → test upload/query → MVP
3. Add US2 → test metrics/dashboard
4. Add US3 → test knowledge ingest/search
5. Add US4 → test agent and report export

### Suggested MVP Scope

- **MVP**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) — upload, parse, store in Loki, session CRUD, log query.
