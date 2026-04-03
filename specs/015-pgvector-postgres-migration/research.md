# Research: Migrate to pgvector and PostgreSQL

**Branch**: `015-pgvector-postgres-migration` | **Date**: 2026-04-03

## 1. PostgreSQL Python Adapter

**Decision**: `psycopg[binary]` (psycopg3) + `psycopg-pool`

**Rationale**:
- psycopg3 is the current-generation PostgreSQL adapter for Python; psycopg2 is in maintenance mode.
- Native async support via `psycopg.AsyncConnection` / `AsyncConnectionPool` — compatible with FastAPI's async handlers.
- The `pgvector-python` library has first-class psycopg3 support with a single `register_vector(conn)` call.
- Built-in connection pooling via the companion `psycopg-pool` package avoids adding a separate dependency like SQLAlchemy.
- The existing raw SQL pattern (parameterized queries) is preserved — no ORM layer added.

**Alternatives considered**:
- `asyncpg`: Faster throughput, but pgvector integration requires manual type codec registration; less straightforward.
- `SQLAlchemy + asyncpg`: ORM overhead not justified; current codebase uses raw SQL with no complex query building.
- `psycopg2`: Maintenance mode; no native async support; less clean pgvector integration.

**Package names**:
```
psycopg[binary,pool]>=3.1   # combined install: driver + pool
pgvector>=0.3
```

---

## 2. pgvector Python Library Integration

**Decision**: Use `pgvector` library with `register_vector()` for psycopg3

**Key integration points**:

```python
import psycopg
from pgvector.psycopg import register_vector

async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
    await register_vector(conn)  # registers the vector type codec
    
    # Insert a vector
    await conn.execute(
        "INSERT INTO embeddings (content, embedding) VALUES (%s, %s)",
        (text, np.array(vector, dtype=np.float32))
    )
    
    # Cosine similarity search (operator: <=>)
    rows = await conn.execute(
        "SELECT content, 1 - (embedding <=> %s) AS score FROM embeddings ORDER BY embedding <=> %s LIMIT %s",
        (np.array(query_vec, dtype=np.float32), np.array(query_vec, dtype=np.float32), top_k)
    )
```

**Key operators**:
- `<=>` — cosine distance (use with `vector_cosine_ops` index)
- `<->` — L2 (Euclidean) distance
- `<#>` — inner product

**register_vector()** must be called per-connection. With a pool, call it in the pool's `configure` callback:

```python
from psycopg_pool import AsyncConnectionPool
from pgvector.psycopg import register_vector_async

pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    min_size=2,        # keep 2 connections warm; adequate for local concurrency
    max_size=5,
    open=False,        # defer open to lifespan startup
    configure=register_vector_async,  # called once per new connection
)

# In FastAPI lifespan — open then wait for min_size connections to be ready:
await pool.open()
await pool.wait()   # ensures pool is ready before serving requests
```

---

## 3. HNSW Index Parameters

**Decision**: HNSW index with `m=16, ef_construction=64`, query-time `SET hnsw.ef_search=40`

**Recommended DDL**:
```sql
CREATE INDEX ON log_chunk_embeddings
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```

**Parameter guidance for ~100K vectors**:

| Parameter | Value | Notes |
|-----------|-------|-------|
| `m` | 16 | Max edges per node; default is 16; increase to 32 for higher recall at cost of memory |
| `ef_construction` | 64 | Index build quality; 64 is a good balance; 128 for higher recall |
| `hnsw.ef_search` | 40 | Query-time beam width; set via `SET hnsw.ef_search = 40` before query, or as session default |

**Recall vs speed**:
- At `m=16, ef_construction=64, ef_search=40`: ~97–99% recall at <100ms for 100K vectors on modern hardware.
- Increasing `ef_search` at query time improves recall at the cost of latency; 40 is suitable for this workload.

**Build time**: HNSW index for 100K 1536-dim vectors takes 2–5 minutes. This is a one-time cost after bulk load.

**Index build note**: For bulk loading, insert all rows first then create the index (faster than inserting with index present).

---

## 4. Connection Pool Configuration

**Decision**: `AsyncConnectionPool(min_size=1, max_size=5)`

**Rationale**: LogPilot is a local developer tool with low concurrency (single user, occasional bursts during log upload). A pool of 1–5 connections balances resource usage with availability.

```python
from psycopg_pool import AsyncConnectionPool
from pgvector.psycopg import register_vector_async

pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=5,
    configure=register_vector_async,
    open=False,  # open explicitly on startup
)

# In FastAPI lifespan:
@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.open()
    yield
    await pool.close()
```

**Timeout**: Default `timeout=30s` is acceptable; no tuning needed for local use.

---

## 5. Docker Image

**Decision**: `pgvector/pgvector:pg16` (official pgvector image)

**Docker Compose service**:
```yaml
postgres:
  image: pgvector/pgvector:pg16
  environment:
    POSTGRES_DB: logpilot
    POSTGRES_USER: logpilot
    POSTGRES_PASSWORD: logpilot
  ports:
    - "5432:5432"
  volumes:
    - postgres-data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U logpilot"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Enabling pgvector** (done once in schema init, not in Docker config):
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Connection string format**:
```
postgresql://logpilot:logpilot@localhost:5432/logpilot
```

**Environment variable**: `DATABASE_URL=postgresql://logpilot:logpilot@postgres:5432/logpilot`

---

## 6. Schema Migration Strategy

**Decision**: Auto-apply schema on startup using idempotent `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` statements.

**Rationale**: LogPilot is a local developer tool. A dedicated migration tool (Alembic, Flyway) adds dependency overhead not justified at this scale. The current SQLite approach uses the same auto-apply pattern.

**Implementation**: A `initialize_schema(pool)` async function runs at application startup, executing all DDL statements. Since we're starting from zero (no existing data), no backward-compatibility migration logic is needed.

---

## 7. Configuration Changes

| Old Variable | New Variable | Notes |
|---|---|---|
| `QDRANT_URL` | _(removed)_ | No longer needed |
| `DATA_DIR` | _(removed)_ | No longer needed |
| _(new)_ | `DATABASE_URL` | Full PostgreSQL connection string |

The `EMBEDDING_DIMENSION` variable is retained and used to define the pgvector column dimension.
