# Data Model: Migrate to pgvector and PostgreSQL

**Branch**: `015-pgvector-postgres-migration` | **Date**: 2026-04-03

All tables are created in the default `public` schema. The `vector` extension must be enabled before table creation.

## Schema Bootstrap

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Table: sessions

Stores session metadata. Maps 1:1 with the existing SQLite `sessions` table.

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    external_link TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Notes**:
- `id` is a client-generated UUID string (existing pattern preserved).
- `TIMESTAMPTZ` replaces SQLite's ISO-format TEXT timestamps.
- No changes to relationships.

---

## Table: reports

Stores AI-generated analysis reports linked to sessions.

```sql
CREATE TABLE IF NOT EXISTS reports (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    question    TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS reports_session_id_idx ON reports(session_id);
```

**Notes**:
- Foreign key with `ON DELETE CASCADE` (if a session is deleted, its reports are deleted too). SQLite had the FK defined but SQLite doesn't enforce FKs by default; PostgreSQL enforces them.
- Index on `session_id` for efficient per-session listing.

---

## Table: session_log_extent

Tracks the nanosecond timestamp range of logs ingested into a session.

```sql
CREATE TABLE IF NOT EXISTS session_log_extent (
    session_id  TEXT PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,
    start_ns    BIGINT NOT NULL,
    end_ns      BIGINT NOT NULL
);
```

**Notes**:
- One row per session (PRIMARY KEY = session_id).
- `start_ns` / `end_ns` are Unix nanoseconds stored as BIGINT (same as SQLite INTEGER).

---

## Table: session_upload_summary

Records statistics about file uploads within a session. One row per uploaded file per session.

```sql
CREATE TABLE IF NOT EXISTS session_upload_summary (
    session_id          TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    uploaded_file_name  TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'pending',
    files_processed     INTEGER NOT NULL DEFAULT 0,
    files_skipped       INTEGER NOT NULL DEFAULT 0,
    lines_parsed        INTEGER NOT NULL DEFAULT 0,
    lines_rejected      INTEGER NOT NULL DEFAULT 0,
    error               TEXT,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (session_id, uploaded_file_name)
);
```

**Notes**:
- Composite primary key `(session_id, uploaded_file_name)` for upsert semantics (same as current SQLite INSERT OR REPLACE behavior).
- PostgreSQL equivalent of upsert: `INSERT ... ON CONFLICT (session_id, uploaded_file_name) DO UPDATE SET ...`.

---

## Table: log_chunk_embeddings

Replaces the Qdrant `logpilot_knowledge` collection. Stores vector embeddings for log chunks with metadata.

```sql
CREATE TABLE IF NOT EXISTS log_chunk_embeddings (
    id              BIGSERIAL PRIMARY KEY,
    session_id      TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    content         TEXT NOT NULL,
    source_path     TEXT,
    document_type   TEXT,
    metadata        JSONB,
    embedding       vector(1536)  -- dimension set by EMBEDDING_DIMENSION config
);

CREATE INDEX IF NOT EXISTS log_chunk_embeddings_session_id_idx
    ON log_chunk_embeddings(session_id);

CREATE INDEX IF NOT EXISTS log_chunk_embeddings_hnsw_idx
    ON log_chunk_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

**Notes**:
- `embedding vector(1536)`: Column dimension is fixed at schema creation time based on `EMBEDDING_DIMENSION` config value (default 1536 for `text-embedding-3-small`). If a different embedding model is configured, the dimension must match.
- `JSONB` for `metadata` replaces Qdrant's arbitrary payload dict; queryable with PostgreSQL JSON operators.
- `document_type` is a top-level column (not buried in JSONB) to enable efficient `WHERE document_type = 'X'` filtering (replaces Qdrant's MatchValue filter).
- `session_id` FK with `ON DELETE CASCADE` — deleting a session removes all its embeddings.
- HNSW index uses `vector_cosine_ops` (cosine similarity). Query operator: `<=>`.
- **Bulk load note**: Insert all rows before creating the HNSW index for faster index builds. For the auto-schema-init path (empty DB on startup), this ordering is not a concern.

---

## Similarity Search Query Pattern

```sql
-- Set query-time HNSW beam width for ~97%+ recall
SET hnsw.ef_search = 40;

-- Top-k cosine similarity search, optionally filtered by document_type
SELECT
    id,
    content,
    source_path,
    document_type,
    metadata,
    1 - (embedding <=> $1) AS score
FROM log_chunk_embeddings
WHERE session_id = $2
  AND ($3::text IS NULL OR document_type = $3)
ORDER BY embedding <=> $1
LIMIT $4;
```

**Parameters**: `$1` = query vector, `$2` = session_id, `$3` = optional document_type filter, `$4` = top_k

---

## Delete All Embeddings for a Session

```sql
DELETE FROM log_chunk_embeddings WHERE session_id = $1;
```

This replaces Qdrant's `delete_collection` / recreate pattern used for re-ingestion.

---

## Entity Relationships

```
sessions (1) ──< reports (N)
sessions (1) ──< session_log_extent (0..1)
sessions (1) ──< session_upload_summary (N)
sessions (1) ──< log_chunk_embeddings (N)
```

All child tables use `ON DELETE CASCADE` — deleting a session removes all associated data.
