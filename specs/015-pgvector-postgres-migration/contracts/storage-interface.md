# Storage Interface Contract

**Branch**: `015-pgvector-postgres-migration` | **Date**: 2026-04-03

## Scope

This is a backend infrastructure change only. The public REST API surface (endpoints, request/response shapes) is **unchanged**. No frontend changes are required.

The contract documented here is the internal storage interface — the boundary between the application logic layer and the storage layer — to ensure the new PostgreSQL-backed implementation satisfies the same contract as the current SQLite + Qdrant implementation.

---

## SessionRepository Contract

All methods previously on `SessionRepository` in `repositories.py` must remain available with identical signatures and semantics.

| Method | Inputs | Returns | Behavior |
|--------|--------|---------|----------|
| `create(session)` | Session object | Session | Inserts a new session row; raises on duplicate id |
| `get(session_id)` | str | Session \| None | Returns session or None if not found |
| `list()` | — | list[Session] | Returns all sessions ordered by created_at DESC |
| `update(session)` | Session object | Session | Updates name/external_link/updated_at |
| `delete(session_id)` | str | None | Deletes session and all cascaded child rows |
| `get_log_extent(session_id)` | str | LogExtent \| None | Returns timestamp range or None |
| `upsert_log_extent(session_id, start_ns, end_ns)` | str, int, int | None | Insert or update log extent |
| `get_upload_summary(session_id)` | str | list[UploadSummary] | Returns all upload records for session |
| `upsert_upload_summary(summary)` | UploadSummary | None | Insert or update by (session_id, filename) |

---

## ReportRepository Contract

| Method | Inputs | Returns | Behavior |
|--------|--------|---------|----------|
| `create(report)` | Report object | Report | Inserts a new report row |
| `get(report_id)` | str | Report \| None | Returns report or None |
| `list_by_session(session_id)` | str | list[Report] | Returns all reports for session, ordered by created_at DESC |
| `update_content(report_id, content)` | str, str | None | Updates content field |

---

## VectorStore Contract

Replaces the Qdrant client (`qdrant_client.py`). New module: `pg_vector_store.py`.

| Method | Inputs | Returns | Behavior |
|--------|--------|---------|----------|
| `upsert_chunks(session_id, chunks)` | str, list[Chunk] | None | Batch-insert embeddings for a session; chunks have: content, embedding, source_path, document_type, metadata |
| `search(session_id, query_vector, top_k, document_type_filter)` | str, list[float], int, str\|None | list[SearchResult] | Returns top-k results ranked by cosine similarity, optionally filtered by document_type |
| `delete_all(session_id)` | str | None | Removes all embeddings for a session (for re-ingestion) |

**SearchResult fields**: `content`, `source_path`, `document_type`, `metadata`, `score` (float, 0–1, higher = more similar)

---

## Configuration Contract

The following environment variables are the new configuration surface:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string: `postgresql://user:pass@host:port/db` |
| `EMBEDDING_DIMENSION` | No | `1536` | Must match the configured embedding model's output dimension |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | OpenAI-compatible embedding model |
| `LLM_BASE_URL` | No | — | OpenAI-compatible LLM base URL |
| `LLM_API_KEY` | No | — | LLM API key |
| `LLM_MODEL` | No | `gpt-4o-mini` | LLM model name |

**Removed variables**: `QDRANT_URL`, `DATA_DIR`

---

## Startup Validation Contract

On application startup, the system MUST:

1. Attempt to connect to PostgreSQL using `DATABASE_URL`.
2. Verify the `vector` extension is installed (`SELECT extname FROM pg_extension WHERE extname = 'vector'`).
3. Create all tables and indexes if they do not exist (idempotent DDL).
4. Refuse to start with a clear error message if (1) or (2) fails.
