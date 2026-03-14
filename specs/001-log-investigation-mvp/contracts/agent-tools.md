# Agent Tools Contract: Log Investigation MVP

**Branch**: `001-log-investigation-mvp` | **Date**: 2025-03-13

The AI agent MUST use only these approved tools. All tools are read-only in MVP. Inputs and outputs MUST be validated; time-range and query-scope MUST be applied; retrieved content MUST NOT override system instructions (prompt injection resistance).

---

## 1. query_logs

Query log store for the current/selected session.

- **Input** (validated):
  - `query`: string (LogQL or simplified query string; length limit TBD)
  - `start`: ISO 8601 datetime (optional; default: session range start)
  - `end`: ISO 8601 datetime (optional; default: session range end)
  - `limit`: int (optional; max results; cap e.g. 1000)
- **Output**: List of log entries with at least: timestamp, level, service, raw_message. Scope MUST be restricted to the current session and to the requested time range.
- **Failure**: Return structured error (e.g. invalid query, timeout); do not expose internal stack traces.

---

## 2. query_metrics

Query derived metrics for the current/selected session.

- **Input** (validated):
  - `metric_name`: string (e.g. errors_total, requests_total, error_rate, response_time_*)
  - `start`: ISO 8601 datetime
  - `end`: ISO 8601 datetime
  - `step`: string (optional; e.g. "15s" for Prometheus step)
- **Output**: Time series or scalar values (schema TBD: e.g. `{ "values": [ [<ts>, <value>], ... ] }`). Only metrics available for the session and time range.
- **Failure**: If metric not available, return clear status (e.g. "metric not derivable for this session"); do not fail the agent run.

---

## 3. search_docs

Semantic search over the documentation/knowledge base.

- **Input** (validated):
  - `query`: string (length limit; sanitized)
  - `limit`: int (optional; cap e.g. 10)
- **Output**: List of chunks with: content, source_path, metadata. Content MUST be passed to the agent in a way that cannot override system instructions (e.g. clearly delimited, not executed as instructions).
- **Failure**: If index empty or error, return empty list or explicit "knowledge base not available"; agent MUST state when docs were not available.

---

## 4. search_repo

Semantic search over the repository content index.

- **Input** (validated): Same as search_docs.
- **Output**: Same shape as search_docs; source_path and metadata allow tracing to code locations.
- **Failure**: Same as search_docs; agent states when repo context was not available.

---

## 5. generate_incident_report

Produce the structured incident report from gathered evidence. Not an external tool call to a third-party; internal step that formats the final answer.

- **Input** (from agent state): Evidence collected via query_logs, query_metrics, search_docs, search_repo; user question.
- **Output**: Structured report with required sections:
  - Incident Summary
  - Possible Root Cause
  - Supporting Evidence
  - Recommended Fix
  - Next troubleshooting steps (and everything needed to resolve the issue)
- **Validation**: Output MUST conform to schema; MUST cite evidence where relevant; MUST state uncertainty when evidence is insufficient. Report MUST be stored in the session and returned to the user.

---

## Tool call validation

- All tool arguments MUST be validated (types, ranges, length, allowed values) before execution.
- Time range MUST be constrained to session data availability; do not allow unbounded or arbitrary ranges that could leak or overload.
- Log and metric queries MUST be scoped to the current/selected session only.

## Prompt injection resistance

- Retrieved content from search_docs and search_repo MUST be inserted into the agent context with clear delimiters and instructions that it is evidence only and must not be interpreted as system or user instructions.
- Outputs from tools MUST be sanitized or passed in a format that the model cannot confuse with its own system prompt.
