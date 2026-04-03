# Quickstart: pgvector + PostgreSQL Backend

**Branch**: `015-pgvector-postgres-migration` | **Date**: 2026-04-03

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for running backend outside Docker)

---

## 1. Configure Environment

Copy the example env file and set required variables:

```bash
cp .env.example .env
```

Minimum required settings in `.env`:

```dotenv
# PostgreSQL (set automatically by Docker Compose; override for external DB)
DATABASE_URL=postgresql://logpilot:logpilot@localhost:5432/logpilot

# LLM (required for AI features)
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your-key-here
LLM_MODEL=openai/gpt-4o-mini

# Embeddings
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

**Note**: `QDRANT_URL` and `DATA_DIR` are no longer used and can be removed from any existing `.env` files.

---

## 2. Start Services

```bash
docker compose up -d
```

This starts:
- `postgres` (pgvector-enabled PostgreSQL on port 5432)
- `loki` (log aggregation on port 3100)
- `prometheus` (metrics on port 9090)
- `grafana` (dashboards on port 3000)
- `backend` (FastAPI on port 8000)

The backend automatically creates all database tables and indexes on first startup.

---

## 3. Verify Startup

Check backend logs to confirm PostgreSQL connection and schema initialization:

```bash
docker compose logs backend --tail=20
```

Expected output:
```
INFO: Connected to PostgreSQL
INFO: pgvector extension verified
INFO: Schema initialized
INFO: Application startup complete
```

Verify the pgvector extension is active:

```bash
docker compose exec postgres psql -U logpilot -d logpilot -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

Expected:
```
 extname | extversion
---------+------------
 vector  | 0.8.0
```

---

## 4. Validate Core Flows

### 4a. Create a session and upload logs

```bash
# Create a session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"name": "test-session"}'

# Note the returned session id
SESSION_ID="<id from above>"

# Upload a log file
curl -X POST "http://localhost:8000/api/sessions/$SESSION_ID/upload" \
  -F "file=@/path/to/your/logfile.log"
```

### 4b. Run a semantic search

```bash
curl -X POST "http://localhost:8000/api/sessions/$SESSION_ID/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "database connection error", "top_k": 5}'
```

Expected: JSON array of matching log chunks with similarity scores.

### 4c. Verify data in PostgreSQL

```bash
docker compose exec postgres psql -U logpilot -d logpilot -c "
SELECT
  (SELECT COUNT(*) FROM sessions) AS sessions,
  (SELECT COUNT(*) FROM reports) AS reports,
  (SELECT COUNT(*) FROM log_chunk_embeddings) AS embeddings;
"
```

---

## 5. Stopping and Resetting

```bash
# Stop all services
docker compose down

# Stop and remove all data volumes (full reset)
docker compose down -v
```

After `down -v`, the next `docker compose up` starts with a fresh empty database.

---

## 6. Troubleshooting

### "pgvector extension not found"

The `pgvector/pgvector:pg16` image includes pgvector pre-installed. If you see this error:
- Verify you are using the correct image: `docker compose images postgres`
- Rebuild the image cache: `docker compose pull postgres`

### "connection refused" on startup

The backend waits for PostgreSQL to be healthy before starting (Docker Compose healthcheck). If the backend fails to connect:
```bash
docker compose ps postgres  # verify postgres is healthy
docker compose restart backend
```

### Embedding dimension mismatch

If you change `EMBEDDING_MODEL` to a model with a different output dimension, you must drop and recreate the `log_chunk_embeddings` table:
```bash
docker compose exec postgres psql -U logpilot -d logpilot -c "DROP TABLE log_chunk_embeddings;"
docker compose restart backend  # schema re-created on startup
```
