# Tasks: Migrate to pgvector and PostgreSQL

**Input**: Design documents from `/specs/015-pgvector-postgres-migration/`  
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅ | quickstart.md ✅

**Tests**: Not explicitly requested — no test tasks generated.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Update dependencies, Docker Compose, and environment configuration before any code changes.

- [x] T001 Update `backend/pyproject.toml`: remove `qdrant-client>=1.17.1`; add `psycopg[binary,pool]>=3.1` and `pgvector>=0.3` to `[project.dependencies]`
- [x] T002 Update `docker-compose.yaml`: remove the `qdrant` service and the `qdrant-data` named volume; add a `postgres` service using image `pgvector/pgvector:pg16` with env vars `POSTGRES_DB=logpilot`, `POSTGRES_USER=logpilot`, `POSTGRES_PASSWORD=logpilot`, port `5432:5432`, volume `postgres-data:/var/lib/postgresql/data`, and a healthcheck (`pg_isready -U logpilot`); add `postgres-data` to the `volumes` block; update the `backend` service to depend on `postgres` being healthy instead of `qdrant`
- [x] T003 [P] Update `.env.example`: remove `QDRANT_URL` and `DATA_DIR` entries; add `DATABASE_URL=postgresql://logpilot:logpilot@localhost:5432/logpilot` with a comment explaining it is the only storage configuration needed

**Checkpoint**: Infrastructure config updated — no application code changed yet

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database connection layer and schema initialization that MUST be complete before any user story work.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Rewrite `backend/app/lib/config.py`: remove the `qdrant_url: str` and `data_dir: Path` settings (and their env var defaults `QDRANT_URL`, `DATA_DIR`); add `database_url: str` field sourced from env var `DATABASE_URL` (no default — required); retain all other existing settings (`llm_*`, `embedding_*`, `knowledge_sources`) unchanged
- [x] T005 Rewrite `backend/app/lib/db.py`: replace all SQLite logic with a psycopg3 sync connection pool; implement `init_pool(database_url)`, `close_pool()`, `get_pool()`, and `_configure_connection()` using `psycopg_pool.ConnectionPool` with `pgvector.psycopg.register_vector` as the configure callback; `min_size=2, max_size=5`
- [x] T006 Add `initialize_schema()` in `backend/app/lib/db.py`: connect via the pool and execute idempotent DDL: `CREATE EXTENSION IF NOT EXISTS vector` (fail fast with clear message if missing), then `CREATE TABLE IF NOT EXISTS` for sessions, reports, session_log_extent, session_upload_summary, and knowledge_chunks (with `vector({EMBEDDING_DIMENSION})` column), plus HNSW index (`USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64)`)
- [x] T007 Add `lifespan` context manager in `backend/app/api/app.py` that calls `init_pool()` and `initialize_schema()` on startup, `close_pool()` on shutdown; pass `lifespan=lifespan` to `FastAPI()`

**Checkpoint**: PostgreSQL pool initializes, schema is created on startup, application starts cleanly with `DATABASE_URL` set

---

## Phase 3: User Story 1 — Unified Database Backend (Priority: P1) 🎯 MVP

**Goal**: All session lifecycle operations (create, read, update, delete) and embedding storage work correctly against PostgreSQL with no SQLite or Qdrant dependency.

**Independent Test**: Start the app with only `DATABASE_URL` set (no `QDRANT_URL`, no `DATA_DIR`), create a session, upload a log file, generate a report, then confirm via psql that rows exist in `sessions`, `session_upload_summary`, `session_log_extent`, and `knowledge_chunks`. Semantic search correctness is verified in Phase 4 (US2).

- [x] T008 [US1] Rewrite `SessionRepository` class in `backend/app/lib/repositories.py`: replace the `get_connection()` / SQLite pattern with `with get_pool().connection() as conn:` in every method; update all parameterized queries to use psycopg3 `%s` placeholders; access rows by index instead of `sqlite3.Row`; update upsert for `session_upload_summary` to use PostgreSQL `INSERT ... ON CONFLICT (session_id) DO UPDATE SET ...`; convert TIMESTAMPTZ columns to ISO strings via `_dt_to_iso()`
- [x] T009 [US1] Rewrite `ReportRepository` class in `backend/app/lib/repositories.py` (same file as T008): replace the SQLite connection pattern with `with get_pool().connection() as conn:`; update all queries for psycopg3 compatibility; convert TIMESTAMPTZ columns to ISO strings
- [x] T010 [US1] Create new file `backend/app/lib/pg_vector_store.py`: implement `upsert_chunks(chunks)` using batched `executemany` INSERT INTO `knowledge_chunks`; implement `delete_all()` with `DELETE FROM knowledge_chunks`; accept `numpy` arrays or lists for the embedding field; use `%s` placeholders throughout
- [x] T011 [US1] Update `backend/app/services/knowledge.py`: replace `from app.lib.qdrant_client import delete_all, upsert_chunks` and `from app.lib.qdrant_client import search as qdrant_search` with imports from `pg_vector_store`; update `search_knowledge` to call `pg_search` instead of `qdrant_search`
- [x] T012 [US1] Delete `backend/app/lib/qdrant_client.py` after confirming no remaining imports reference it

**Checkpoint**: Full session lifecycle works end-to-end in PostgreSQL; no Qdrant or SQLite dependency remains at runtime

---

## Phase 4: User Story 2 — Semantic Search (Priority: P2)

**Goal**: Similarity search returns correct, ranked results using the pgvector HNSW index.

**Independent Test**: Ingest a known set of log documents (at least 10 chunks), run a natural-language query known to match specific chunks, verify the top result is the correct chunk, verify response time is under 2 seconds.

- [x] T013 [US2] Implement `search(query_embedding, limit, document_type_filter)` in `backend/app/lib/pg_vector_store.py`: execute `SET hnsw.ef_search = 40` before the similarity query; use the cosine distance operator `<=>` in `ORDER BY`; apply `WHERE document_type = %s` or `WHERE document_type = ANY(%s)` for list filters; return dicts with `content`, `source_path`, `document_type`, `metadata`, `score` (where `score = 1 - distance`); handle empty result gracefully
- [x] T014 [US2] Verify all search call sites in `backend/` correctly call `pg_search` through `knowledge_service.search_knowledge()` — confirmed via grep, no direct qdrant search calls remain

**Checkpoint**: Semantic search returns ranked results; similarity scores are in [0, 1] range; empty knowledge base returns `[]` without error

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, documentation, and final validation.

- [x] T015 [P] Update `.specify/memory/constitution.md`: replace `Qdrant for vector search` with `PostgreSQL with pgvector for vector search and session data storage`; bump version to 1.0.1 and update `Last Amended` date
- [x] T016 [P] Audit `backend/pyproject.toml` for any remaining `qdrant` references — confirmed clean
- [ ] T017 Run the quickstart validation from `specs/015-pgvector-postgres-migration/quickstart.md`: `docker compose up -d`, confirm backend logs show "pgvector extension verified" and "Schema initialized", run the curl commands for session creation, log upload, and similarity search, run the psql verification query to confirm record counts are non-zero
- [x] T018 [P] No `docs/PRD.md` Qdrant references found that require update (constitution updated in T015)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately; T002 and T003 can run in parallel with T001
- **Foundational (Phase 2)**: Depends on Phase 1 complete; T005, T006, T007 must run sequentially (T005 → T006 → T007); T004 can run in parallel with T005
- **US1 (Phase 3)**: Depends on Phase 2 complete; T008 → T009 (same file); T010 and T011 can start in parallel after T008/T009 since they are different files
- **US2 (Phase 4)**: Depends on Phase 3 complete; T013 then T014 sequentially
- **Polish (Phase 5)**: Depends on Phase 4; T015, T016, T018 can run in parallel; T017 runs last

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependency on US2
- **US2 (P2)**: Depends on US1 completion (search builds on the same `pg_vector_store.py` file)

### Within Each Phase

- Phase 2: T004 [P with T005] → T005 → T006 → T007
- Phase 3: T008 → T009 (same file) → T010 [P with T011] → T011 → T012
- Phase 4: T013 → T014
- Phase 5: T015 [P] | T016 [P] | T018 [P] → T017 (validation last)

---

## Parallel Execution Examples

### Phase 1 Parallel

```
Parallel:
  Task T001: Update pyproject.toml
  Task T002: Update docker-compose.yaml
  Task T003: Update .env.example
```

### Phase 2 Parallel Start

```
Parallel:
  Task T004: Update config.py
  Task T005: Rewrite db.py (pool + init_pool)
Then sequential:
  Task T006: Add initialize_schema() to db.py
  Task T007: Wire lifespan in api/app.py
```

### Phase 3 Parallel Window

```
Sequential:
  Task T008: Rewrite SessionRepository
  Task T009: Rewrite ReportRepository
Then parallel:
  Task T010: Create pg_vector_store.py
  Task T011: Update imports across backend
Then sequential:
  Task T012: Delete qdrant_client.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T003) ✅
2. Complete Phase 2: Foundational (T004–T007) ✅
3. Complete Phase 3: User Story 1 (T008–T012) ✅
4. **STOP and VALIDATE**: Start app, create session, upload logs, confirm data in PostgreSQL
5. All core functionality is restored — semantic search is the next increment

### Incremental Delivery

1. Phase 1 + Phase 2 → PostgreSQL pool working, schema initialized ✅
2. Phase 3 → Session/report/embedding CRUD working end-to-end (no Qdrant) ✅
3. Phase 4 → Semantic search working via pgvector HNSW ✅
4. Phase 5 → Clean, documented, validated (T017 pending docker compose up)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks in the same phase
- psycopg3 uses `%s` placeholders (same as psycopg2 / current code) — no query syntax rewrite needed
- Sync `ConnectionPool` used (not `AsyncConnectionPool`) — codebase is predominantly synchronous
- Knowledge embeddings are global (not session-scoped) — table `knowledge_chunks` has no session FK
- `register_vector` is called per-connection via the pool `configure` callback
- The HNSW index is created in T006 as part of schema init; index build on first populate is automatic
- Constitution updated in T015 to reflect Qdrant → pgvector technology change (v1.0.1)
