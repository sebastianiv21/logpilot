# Feature Specification: Migrate to pgvector and PostgreSQL

**Feature Branch**: `015-pgvector-postgres-migration`  
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: User description: "i want to move the current architecture to use pgvector for embeddings and postgres for session data"

## Clarifications

### Session 2026-04-03

- Q: Is data migration from SQLite and Qdrant required? → A: No — starting from zero, no existing data needs to be preserved.
- Q: What vector index strategy should be used for similarity search? → A: HNSW approximate index.
- Q: Where will PostgreSQL be deployed? → A: Local Docker Compose only — pgvector container replacing Qdrant.
- Q: What connection pooling strategy is needed? → A: Simple built-in pool (1–5 connections managed by the DB client).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unified Database Backend (Priority: P1)

As a system operator, I want all persistent data (session metadata, reports, log extents, upload summaries, and vector embeddings) to be stored in a single PostgreSQL instance so that I only need to operate, back up, and monitor one database.

**Why this priority**: Consolidating from two separate storage engines (SQLite + Qdrant) into one PostgreSQL instance dramatically reduces operational complexity, removes the need to run a dedicated Qdrant service, and enables standard database tooling for backup, monitoring, and recovery.

**Independent Test**: Can be fully tested by starting the application with only a PostgreSQL connection configured (no Qdrant, no SQLite file), performing a session lifecycle (create session → upload logs → generate a report), and verifying that session records, log extents, upload summaries, and embedding rows are all persisted and retrievable from PostgreSQL alone. Semantic search quality is validated independently in User Story 2.

**Acceptance Scenarios**:

1. **Given** a fresh PostgreSQL instance with the pgvector extension enabled, **When** the application starts for the first time, **Then** all required tables and vector indexes are created automatically without manual intervention.
2. **Given** the application is running with PostgreSQL, **When** a user creates a session and uploads log data, **Then** session records, log extents, and upload summaries are persisted in PostgreSQL tables.
3. **Given** the application is running with PostgreSQL and pgvector, **When** log chunks are embedded and stored, **Then** vector data is stored in a pgvector-enabled column and similarity searches return ranked results correctly.
4. **Given** a configured PostgreSQL connection string, **When** the application starts, **Then** no Qdrant URL or SQLite file path configuration is required.

---

### User Story 2 - Semantic Search Continues to Work (Priority: P2)

As a user querying logs, I want semantic similarity search to return the same quality of results as before so that my log analysis workflow is unaffected by the infrastructure change.

**Why this priority**: The correctness of vector similarity search is the core value proposition of the RAG feature. Any regression here would directly degrade user experience.

**Independent Test**: Can be tested independently by ingesting a fixed set of log documents, running a known query, and asserting that the top-N results match expected log chunks by cosine similarity.

**Acceptance Scenarios**:

1. **Given** log chunks are stored as embeddings in pgvector, **When** a user submits a natural-language query, **Then** the system returns the most semantically relevant log chunks ranked by cosine similarity.
2. **Given** an empty vector store for a session, **When** a similarity search is executed, **Then** the system returns an empty result set without errors.
3. **Given** a large number of embedded log chunks, **When** a similarity search is executed, **Then** results are returned within an acceptable time (under 2 seconds for up to 100,000 vectors).

---

### Edge Cases

- What happens when the PostgreSQL connection is unavailable at startup? The application should surface a clear error and refuse to start rather than falling back to SQLite.
- What happens when the pgvector extension is not installed on the PostgreSQL instance? The application should detect this and emit a human-readable error message.
- What happens when an embedding vector dimension in pgvector does not match the configured embedding model dimension? The system should reject the mismatch on startup or schema creation.
- How does the system handle concurrent writes to the same session from multiple requests? PostgreSQL's transactional guarantees should prevent data corruption.
- What happens when a similarity search is run against a session that has no embedded vectors yet? Should return empty results gracefully.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store session metadata, reports, log extents, and upload summaries in PostgreSQL tables with equivalent schemas to the current SQLite tables.
- **FR-002**: System MUST store log chunk embeddings in a pgvector-enabled PostgreSQL column, replacing the Qdrant collection.
- **FR-003**: System MUST perform vector similarity search (cosine distance) against embeddings stored in pgvector, using an HNSW approximate index to meet performance targets at scale.
- **FR-004**: System MUST automatically apply the database schema (tables and vector indexes) on first startup if they do not exist.
- **FR-005**: System MUST be configurable via a single PostgreSQL connection string, replacing the separate Qdrant URL and SQLite file path settings.
- **FR-010**: System MUST manage database connections using a small built-in connection pool (1–5 connections); no external connection pooler is required.
- **FR-006**: System MUST remove the runtime dependency on the Qdrant service; no Qdrant client or URL should be required to operate the application.
- **FR-007**: System MUST validate on startup that the pgvector extension is enabled on the connected PostgreSQL instance and emit a clear error if it is not.
- **FR-008**: System MUST enforce that the configured embedding vector dimension matches the dimension of the pgvector column at schema creation time.
- **FR-009**: Data migration from existing SQLite or Qdrant stores is explicitly out of scope; the system assumes a fresh PostgreSQL instance with no pre-existing data.

### Key Entities

- **Session**: Represents an analysis session with metadata (identifier, name, optional external link, timestamps).
- **Report**: A generated analysis report associated with a session (content, originating question, timestamps).
- **SessionLogExtent**: Tracks the timestamp range of logs ingested into a session (earliest and latest log timestamps).
- **SessionUploadSummary**: Records metadata about file uploads within a session (filename, parse statistics).
- **LogChunkEmbedding**: A vector embedding of a log chunk, associated with a session, including the original text and metadata payload.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All existing application features (session creation, log upload, semantic search, report generation) work correctly with PostgreSQL and pgvector as the only storage backend.
- **SC-002**: Semantic similarity search returns results in under 2 seconds for a dataset of up to 100,000 embedded log chunks, using an HNSW approximate index with at least 95% recall accuracy.
- **SC-003**: The application starts successfully with a valid PostgreSQL connection string and no Qdrant or SQLite configuration present.
- **SC-004**: The number of external services required to run the application decreases by one (Qdrant is eliminated), reducing infrastructure overhead.
- **SC-005**: All automated tests pass with the new PostgreSQL-backed storage layer.

## Assumptions

- The target PostgreSQL version supports the pgvector extension (PostgreSQL 14+ assumed).
- The embedding model and its vector dimension remain unchanged during this migration; only the storage backend changes.
- A PostgreSQL instance (or managed service) is available and accessible to the backend at deployment time.
- No existing data needs to be preserved; the system starts fresh with an empty PostgreSQL database.
- This change does not affect the Loki or Prometheus integrations, which remain read-only external data sources.
- PostgreSQL is deployed via Docker Compose only (local development). A pgvector-enabled PostgreSQL container replaces the Qdrant container in the existing Docker Compose setup. Managed cloud PostgreSQL services are out of scope.
