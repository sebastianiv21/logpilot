# Implementation Plan: Migrate to pgvector and PostgreSQL

**Branch**: `015-pgvector-postgres-migration` | **Date**: 2026-04-03 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/015-pgvector-postgres-migration/spec.md`

## Summary

Replace the two existing storage backends (SQLite for relational data, Qdrant for vector embeddings) with a single PostgreSQL instance using the pgvector extension. The backend's relational tables (sessions, reports, session_log_extent, session_upload_summary) migrate to PostgreSQL; the Qdrant collection (logpilot_knowledge) becomes a pgvector-enabled table with an HNSW cosine index. No existing data migration is required — the system starts fresh. The Qdrant Docker Compose service is removed and replaced with a pgvector-enabled PostgreSQL container.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, psycopg[binary,pool] (psycopg3 + pool), pgvector (Python client)  
**Storage**: PostgreSQL 16 with pgvector extension (replaces SQLite + Qdrant)  
**Testing**: pytest (existing test suite)  
**Target Platform**: Linux Docker container (local Docker Compose only)  
**Project Type**: web-service (FastAPI backend)  
**Performance Goals**: Vector similarity search < 2 seconds for up to 100,000 embedded chunks  
**Constraints**: HNSW approximate index (cosine ops); small connection pool (min 1, max 5); no ORM  
**Scale/Scope**: Local single-user/team deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Local-First** ✅: PostgreSQL runs as a Docker Compose container; no cloud egress introduced.
- **Observability-First** ✅: Loki and Prometheus integrations are unchanged; this change only affects storage.
- **Evidence-Backed AI** ✅: AI tool layer is unchanged; only the underlying storage for knowledge chunks changes.
- **User Stories** ✅: Spec has two independently testable user stories (P1: unified backend, P2: semantic search).
- **Simplicity** ✅: Replacing two services with one reduces complexity; raw SQL pattern preserved (no ORM added).

**⚠️ Constitution Technology Constraint Override**: The constitution (v1.0.0) names Qdrant as the designated vector store. This feature deliberately replaces Qdrant with pgvector. Justification documented in Complexity Tracking below.

### Post-Design Re-check (Phase 1 complete)

- **Local-First** ✅: `pgvector/pgvector:pg16` Docker image; no cloud egress.
- **Observability-First** ✅: Loki, Prometheus, Grafana services unchanged.
- **Evidence-Backed AI** ✅: Tool layer unchanged; only storage backend changes.
- **User Stories** ✅: Two independently testable stories with acceptance criteria.
- **Simplicity** ✅: Net service reduction (2 → 1 storage backend); no ORM added; raw SQL pattern preserved.

## Project Structure

### Documentation (this feature)

```text
specs/015-pgvector-postgres-migration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal — no public API changes)
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (affected files)

```text
backend/
├── app/
│   └── lib/
│       ├── config.py              # Remove QDRANT_URL/DATA_DIR; add DATABASE_URL
│       ├── db.py                  # Replace SQLite logic with psycopg3 PostgreSQL client
│       ├── repositories.py        # Update queries (parameterization style: %s → $1)
│       └── qdrant_client.py       # Replace with pg_vector_store.py (pgvector queries)
└── pyproject.toml                 # Add psycopg[binary], psycopg-pool, pgvector deps
                                   # Remove qdrant-client dep

docker-compose.yaml                # Remove qdrant service; add postgres service (pgvector image)
.env.example                       # Replace QDRANT_URL/DATA_DIR with DATABASE_URL
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| Replacing Qdrant (constitution-designated vector store) | Reduces operational services from 2 storage backends to 1; pgvector is sufficient for local-scale vector search and eliminates a dedicated service | Keeping Qdrant maintains the current 2-backend complexity; for local-only deployment at <100K vectors, pgvector delivers acceptable performance without a dedicated vector database service |
