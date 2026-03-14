# Research: Log Investigation MVP

**Branch**: `001-log-investigation-mvp` | **Date**: 2025-03-13

Consolidated findings for Phase 0. All Technical Context items are resolved; no NEEDS CLARIFICATION remain.

---

## 1. Pushing Logs to Loki from Python

**Decision**: Use Loki HTTP push API (`POST /loki/api/v1/push`) from the backend. Prefer a small custom client or the `python-logging-loki-v2` handler pattern (push with labels and nanosecond timestamps) rather than running Promtail as a sidecar for this use case.

**Rationale**: Backend ingests logs in-process after parsing; pushing directly to Loki keeps the pipeline simple and avoids extra processes. The push payload is well-documented: streams with labels and `[[timestamp_ns, line], ...]`.

**Alternatives considered**: Promtail scraping log files written by the backend — adds file I/O and delay; acceptable for high-volume production but not required for MVP. Using a logging handler (python-logging-loki-v2) — good fit if we standardize on Python logging; otherwise a minimal `httpx`/`requests` client to POST JSON to the push endpoint is sufficient.

---

## 2. Safe Archive Extraction (Path Traversal)

**Decision**: Do not use `ZipFile.extractall()` without validation. For each entry, resolve the extraction path with `pathlib.Path(base_dir, entry_name).resolve()` and ensure it `is_relative_to(base_dir)` (Python 3.9+) before writing. Extract only into a dedicated temp directory; reject or skip entries that resolve outside that directory.

**Rationale**: Path traversal via names like `../etc/passwd` or `..\\config` is a known risk. The standard library does not fully sanitize names in all Python versions; caller must validate.

**Alternatives considered**: Relying on `zipfile.Path` — documentation states the caller is responsible for sanitization. Using a single `extractall` with a sanitized copy of the zip — possible but more complex; per-entry validation is clear and auditable.

---

## 3. Configurable LLM Provider (OpenAI-Compatible)

**Decision**: Use the official `openai` Python package with `OpenAI(base_url=..., api_key=...)`. Configure base URL and API key via environment or config (e.g. `OPENAI_API_BASE`, `OPENAI_API_KEY` or `LLM_BASE_URL`, `LLM_API_KEY`). No hardcoded vendor; same client works for OpenAI, OpenRouter, or any OpenAI-compatible endpoint.

**Rationale**: OpenAI SDK supports custom `base_url`; OpenRouter and most gateways expose an OpenAI-compatible API. Single client interface keeps the agent code provider-agnostic.

**Alternatives considered**: OpenRouter-specific SDK — adds a second integration path; not needed if OpenRouter is used via OpenAI-compatible base URL. Multiple client implementations — YAGNI; one configurable client suffices for MVP.

---

## 4. Log Parsing (Plain Text, JSON, Application Log Lines)

**Decision**: Use a small pattern registry: (1) Try JSON parse per line; if valid JSON, map known fields (timestamp, level, message, etc.) to normalized schema. (2) For non-JSON, try a set of regex patterns with named groups (e.g. timestamp, level, message); use the first match. (3) Preserve raw line in all cases; for unmatched lines, set timestamp to ingest time and level to “unknown” and still store. Report counts of parsed vs rejected lines in the upload result.

**Rationale**: Matches spec (common formats, mixed parseable/unparseable, no full-upload failure on partial parse). Multi-pattern approach is a common best practice; ordering (JSON first, then regex) keeps logic simple.

**Alternatives considered**: Single rigid regex — too brittle for varied formats. External log parser library — adds dependency; MVP can start with a few documented patterns and extend later.

---

## 5. Session and Report Metadata Store

**Decision**: Use SQLite for session and report metadata (session id, name, external link, created_at; report id, session_id, content, created_at). File path: under a configured data directory (e.g. `./data/logpilot.db`). No separate DB server for MVP.

**Rationale**: Single file, no extra process; sufficient for session history, report history, and “current session” selection. Logs and metrics remain in Loki/Prometheus; knowledge index in Qdrant.

**Alternatives considered**: JSON/files per session — works but harder to query and to keep consistent. PostgreSQL — overkill for local MVP; can replace SQLite later if needed.

---

## 6. Archive Structure Conventions (Service / Environment Labels)

**Decision**: Document one primary convention: path-based segments such as `logs/<service>/<optional_env>/...` or `logs/<service>/...`. Parse the first path segment after a known prefix as `service`; second as `environment` if present. If structure does not match (flat archive or unknown cloud export), use a single upload-scoped label (e.g. `service=upload` or `service=<archive_basename>`) so all logs remain queryable. Document in quickstart and API docs.

**Rationale**: Aligns with spec clarifications: path-based when possible; fallback to single label; environment optional when not present in path.

**Alternatives considered**: No fallback — would leave some uploads unqueryable. Heuristic detection of cloud formats — defer to post-MVP; MVP uses documented convention + single-label fallback.

---

## 7. Report Export (Markdown and PDF)

**Decision**: Markdown: return or stream the stored report content (already structured text). PDF: use a library such as `weasyprint` or `reportlab` to render Markdown (or HTML derived from Markdown) to PDF. Export is a synchronous or async endpoint that returns the file for the selected report and format; no client-side generation required for MVP.

**Rationale**: Report content is stored per session; export is a format conversion plus download. Server-side PDF keeps client simple and ensures consistent layout.

**Alternatives considered**: Client-side PDF (e.g. browser print) — depends on frontend; spec allows backend-driven export. External service for PDF — unnecessary for local-first MVP.
