# logpilot Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-03

## Active Technologies
- Python 3.11+ + FastAPI, psycopg[binary] (psycopg3), psycopg-pool, pgvector (Python client) (015-pgvector-postgres-migration)
- PostgreSQL 16 with pgvector extension (replaces SQLite + Qdrant) (015-pgvector-postgres-migration)

- TypeScript 5.9 + React 19 (frontend), Python 3.14 (backend) + Frontend: Vite, React Router, TanStack Query, React Hook Form, Zod, ReactMarkdown, DaisyUI, Tailwind, Sonner, Lucide React; Backend: FastAPI, Pydantic, markdown, ReportLab, sqlite3 (014-report-followups)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

TypeScript 5.9 + React 19 (frontend), Python 3.14 (backend): Follow standard conventions

## Recent Changes
- 015-pgvector-postgres-migration: Added Python 3.11+ + FastAPI, psycopg[binary] (psycopg3), psycopg-pool, pgvector (Python client)

- 014-report-followups: Added TypeScript 5.9 + React 19 (frontend), Python 3.14 (backend) + Frontend: Vite, React Router, TanStack Query, React Hook Form, Zod, ReactMarkdown, DaisyUI, Tailwind, Sonner, Lucide React; Backend: FastAPI, Pydantic, markdown, ReportLab, sqlite3

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
