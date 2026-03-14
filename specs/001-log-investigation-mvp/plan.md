# Implementation Plan: Log Investigation Platform MVP

**Branch**: `001-log-investigation-mvp` | **Date**: 2025-03-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-log-investigation-mvp/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a local-first log investigation platform that accepts compressed log archives, parses and normalizes logs into Loki, derives metrics for Prometheus, provisions Grafana dashboards, indexes documentation/repo content in Qdrant, and provides an AI agent that uses only approved tools to produce structured incident reports. Full stack runs via Docker Compose; sessions scope logs and metrics; reports are stored per session and exportable as Markdown or PDF.

## Technical Context

**Language/Version**: Python 3.11+ (typed)  
**Primary Dependencies**: FastAPI, Loki client (e.g. promtail or push API), Prometheus client, Grafana provisioning API, Qdrant client, OpenAI-compatible LLM client (configurable base URL + API key)  
**Storage**: Loki (log store), Prometheus (metrics), Qdrant (vector index for knowledge base); session and report metadata in SQLite or file-based store for MVP  
**Testing**: pytest, contract tests for API and tool schemas  
**Target Platform**: Linux (Docker Compose), local development  
**Project Type**: web-service (backend API; Grafana as primary dashboard UI; optional minimal web UI for upload/session/report export)  
**Performance Goals**: Medium-sized log archives; interactive upload-to-query latency after ingestion  
**Constraints**: Archive limit 500 MB uncompressed / 100 MB compressed; read-only AI tools; sanitized extraction paths  
**Scale/Scope**: Single-user / team local investigation; session-scoped data

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md`:

- **Local-First**: Design supports local deployment (e.g., Docker Compose); no mandatory cloud egress. **PASS** — full stack runs locally; LLM configurable (user-supplied API key).
- **Observability-First**: Logs → queryable store (Loki); metrics derived and exposed (Prometheus); dashboards provisioned (Grafana). **PASS** — spec and PRD align.
- **Evidence-Backed AI**: Agent uses only approved tools; structured output; no production remediation. **PASS** — FR-010, FR-011, FR-012 and constitution list same tools and structure.
- **User Stories**: Feature is specified as independently testable user stories with acceptance criteria. **PASS** — P1–P4 stories with scenarios in spec.
- **Simplicity**: Scope within PRD; extra complexity documented in Complexity Tracking table below. **PASS** — MVP bounded; no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-log-investigation-mvp/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/          # Domain models, session, log record, report
│   ├── services/        # Upload, parsing, ingestion, metrics, knowledge, agent
│   ├── api/             # FastAPI routes: upload, sessions, reports, export
│   ├── lib/             # Shared utilities, Loki/Prometheus/Qdrant clients
│   └── main.py          # FastAPI app entry (run: uv run fastapi dev app/main.py)
└── tests/
    ├── contract/        # API and tool schema contracts
    ├── integration/
    └── unit/

docker/                  # Dockerfile(s), Grafana provisioning configs
docker-compose.yaml      # At root: Loki, Prometheus, Grafana, Qdrant, backend
```

**Structure Decision**: Backend-focused Python service with Docker Compose for Loki, Prometheus, Grafana, and Qdrant. Grafana provides dashboard UI; backend API provides upload, session management, knowledge ingestion, agent invocation, and report export. Optional minimal web UI can be added later for upload/session/report without changing core architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |
