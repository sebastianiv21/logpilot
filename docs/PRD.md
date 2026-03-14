# PRD: AI-Powered Log Investigation Platform

## 1. Overview

### Product Name
AI-Powered Log Investigation Platform

### Product Summary
A local-first DevOps platform that lets engineers upload compressed application logs, transform them into searchable observability data, and use an AI agent to analyze incidents using logs, derived metrics, repository context, and internal documentation.

The product is designed as a simplified AI-powered observability system for engineering teams that need faster incident investigation and clearer root-cause analysis.

### Problem Statement
When incidents occur, engineers often need to manually switch between raw log files, dashboards, runbooks, and source code repositories to understand what failed and why. This process is slow, fragmented, and highly dependent on individual expertise.

Teams need a system that can:
- ingest raw logs quickly,
- normalize and visualize operational signals,
- correlate logs with metrics and knowledge sources,
- and assist with root-cause investigation using AI.

### Vision
Enable DevOps and platform engineers to move from raw incident data to an evidence-backed incident explanation in minutes rather than hours.

---

## 2. Goals

### Primary Goals
- Allow users to upload `.zip` files containing application logs.
- Parse and ingest logs into a queryable log system.
- Derive operational metrics from logs and expose them in dashboards.
- Provide a unified interface for logs, metrics, and AI-assisted investigation.
- Let an AI agent investigate incidents using logs, metrics, repository context, and documentation.
- Produce structured root-cause analysis reports with evidence.

### Success Criteria
- A user can upload a `.zip` log bundle and view parsed logs in the platform.
- The system generates and stores derived metrics such as error counts and request volume.
- Grafana dashboards are provisioned automatically and usable without manual setup.
- The AI agent can answer incident questions using tool calls across logs, metrics, docs, and repository knowledge.
- The agent returns a structured incident report with summary, likely cause, supporting evidence, and recommended next steps.

### Non-Goals (MVP)
- Full enterprise-scale multi-tenant observability.
- Real-time cluster-wide Kubernetes ingestion.
- Automatic code fixes or production remediation.
- Broad SIEM or security analytics scope.
- Full CI/CD, RBAC, SSO, or organization management.

---

## 3. Target Users

### Primary Users
- DevOps engineers
- Site Reliability Engineers (SREs)
- Platform engineers
- Backend engineers investigating service failures

### Secondary Users
- Engineering managers reviewing incident findings
- QA or support engineers performing basic incident triage

### User Needs
- Upload log archives without manual preprocessing.
- Search logs by service, environment, severity, and time.
- See error spikes and traffic patterns visually.
- Ask natural-language questions about incidents.
- Receive evidence-backed explanations instead of vague summaries.

---

## 4. User Stories

### Log Ingestion
- As an engineer, I want to upload a `.zip` file of logs so that I can investigate an incident without manually reformatting files.
- As an engineer, I want the system to detect common log formats automatically so that upload works across multiple applications.

### Observability
- As an engineer, I want parsed logs stored with useful labels so that I can filter by service, environment, and severity.
- As an engineer, I want metrics derived from logs so that I can identify spikes, anomalies, and failure windows.
- As an engineer, I want prebuilt dashboards so that I can inspect system health immediately after upload.

### Knowledge Retrieval
- As an engineer, I want the system to search documentation and runbooks so that historical knowledge informs the investigation.
- As an engineer, I want repository context to be searchable so that the AI can connect incidents to related modules or code paths.

### AI Investigation
- As an engineer, I want to ask questions such as "Why did the service fail yesterday?" so that I can get a concise root-cause analysis.
- As an engineer, I want the AI to cite evidence from logs, metrics, docs, and code so that I can trust the response.
- As an engineer, I want the AI to stay within approved tools and produce structured output so that investigations are safe and predictable.

---

## 5. Core Use Case

### Primary Workflow
1. User uploads a compressed log archive.
2. Platform extracts files and detects log formats.
3. Platform parses and normalizes log lines.
4. Logs are ingested into Loki with queryable labels.
5. Metrics are derived and exposed to Prometheus.
6. Grafana dashboards show log and metric trends.
7. Documentation and repository content are indexed into Qdrant.
8. User asks an incident question.
9. AI agent queries logs, metrics, docs, and repository context.
10. AI agent returns a structured incident report.

### Example Prompt
"Why did the service fail yesterday?"

### Expected Agent Behavior
- Query logs for errors in the relevant time window.
- Inspect derived metrics for spikes, drops, or anomalies.
- Search runbooks and documentation for similar symptoms.
- Search repository context for relevant modules, handlers, or recent logic.
- Produce a reasoned explanation with supporting evidence.

---

## 6. Functional Requirements

### 6.1 Log Upload Service
The system must provide a `POST /logs/upload` endpoint.

#### Requirements
- Accept `.zip` uploads.
- Extract one or more log files from the archive.
- Reject unsupported or malformed archives gracefully.
- Support common log formats including:
  - plain text logs,
  - JSON logs,
  - typical application log lines.
- Return upload status, parsing summary, and ingestion result.

#### Acceptance Criteria
- Uploading a valid `.zip` succeeds through the API.
- The response includes number of files processed, lines parsed, and lines rejected.
- Invalid archives return a structured error message.

### 6.2 Log Processing Pipeline
The system must parse, normalize, and enrich uploaded log lines before ingestion.

#### Requirements
- Parse timestamps where possible.
- Extract or infer log level.
- Extract or infer service name.
- Normalize records into a canonical internal schema.
- Apply labels for Loki queries.
- Preserve raw log message content for evidence review.

#### Required Labels
- `service`
- `environment`
- `log_level`

#### Acceptance Criteria
- Parsed logs can be queried by label and time range.
- Unparseable lines are tracked and reported without failing the whole upload.
- Normalized records preserve source filename and ingestion batch metadata.

### 6.3 Log Storage
The system must store logs in Loki for querying and visualization.

#### Requirements
- Push normalized log records into Loki.
- Support querying by label selectors and time ranges.
- Enable use from both Grafana and the AI tool layer.

#### Acceptance Criteria
- Uploaded logs appear in Grafana Explore or dashboard panels.
- AI log queries use the same underlying log source as the observability interface.

### 6.4 Metrics Generation
The system must derive metrics from ingested logs.

#### Initial Metrics
- `errors_total`
- `requests_total`
- `error_rate`
- `response_time_distribution` (when latency is present in logs)

#### Requirements
- Convert parsed log events into Prometheus-compatible metrics.
- Expose metrics for visualization in Grafana.
- Support time-window analysis around incidents.

#### Acceptance Criteria
- Metrics are queryable after log ingestion.
- Dashboard panels reflect generated metrics without manual configuration.
- Missing fields in logs do not break metrics generation; unsupported metrics are skipped with status feedback.

### 6.5 Grafana Dashboards
The system must auto-provision dashboards for uploaded log data.

#### Required Dashboard Views
- error rate
- request volume
- error distribution
- log volume
- anomalies over time

#### Requirements
- Provision dashboards automatically on startup.
- Provide at least one default dashboard for uploaded application data.
- Support correlation between metric panels and log exploration.

#### Acceptance Criteria
- A fresh local setup includes working dashboards.
- Users can inspect metrics and pivot to logs for the same period.

### 6.6 Knowledge Base (RAG)
The system must ingest documentation, runbooks, and repository content into a searchable vector index.

#### Requirements
- Support ingestion of markdown, text, and source code files.
- Chunk content into retrievable segments.
- Generate embeddings for each chunk.
- Store embeddings and metadata in Qdrant.
- Preserve source metadata such as file path, repository, and document type.

#### Acceptance Criteria
- Relevant documentation and code snippets can be retrieved for incident questions.
- Retrieved results include source references and metadata.

### 6.7 LLM / Model Provider (Provider-Agnostic)
The system must support configurable LLM backends and must not be locked to a single model provider.

#### Requirements
- Support at least one of: OpenAI API, OpenRouter, or any OpenAI-compatible HTTP API (e.g., other gateways or self-hosted models).
- Model provider, model name, base URL, and API key must be configurable via environment or configuration (no hardcoded vendor).
- Use a single, provider-agnostic client interface (e.g., OpenAI SDK with configurable base URL) so that switching providers does not require code changes.
- Document supported providers and required configuration (e.g., OpenRouter model IDs, base URLs) in setup or deployment docs.

#### Acceptance Criteria
- A user can run the AI agent using OpenAI by setting the appropriate API key and optional base URL.
- A user can run the AI agent using OpenRouter (or another compatible gateway) by setting base URL and API key only.
- Changing provider or model is a configuration change, not a code or deployment change.

### 6.8 AI Investigation Agent
The system must provide an AI agent that can investigate incidents using approved tools.

#### Required Tools
- `query_logs(query)`
- `query_metrics(metric_name, time_range)`
- `search_docs(query)`
- `search_repo(query)`
- `generate_incident_report(data)`

#### Requirements
- Support natural-language incident questions.
- Use tool-based reasoning rather than free-form hallucinated responses.
- Produce structured output with these sections:
  - Incident Summary
  - Possible Root Cause
  - Supporting Evidence
  - Recommended Fix
- Preserve intermediate evidence for auditability.

#### Acceptance Criteria
- The agent can answer a representative incident question end-to-end.
- The final answer references logs, metrics, and at least one knowledge source when relevant.
- Reports follow the required structure consistently.

### 6.9 AI Guardrails
The system must protect the agent workflow from unsafe or invalid behavior.

#### Requirements
- Structured outputs for final reports.
- Validation of tool inputs and outputs.
- Prompt injection resistance for retrieved content.
- Limited tool permissions.
- Time-range and query-scope controls.
- Clear fallback responses when evidence is insufficient.

#### Acceptance Criteria
- Tool calls are schema-validated.
- Retrieved documents cannot directly override system instructions.
- The agent returns uncertainty explicitly when evidence is weak.

---

## 7. Non-Functional Requirements

### Architecture
- Must run locally with Docker Compose.
- Must be modular and extensible.
- Must follow clean architecture principles.
- Must use typed Python code.
- LLM integration must be abstracted behind a configurable client (base URL + API key + model) so that OpenAI, OpenRouter, or any OpenAI-compatible endpoint can be used without code changes.

### Reliability
- Upload failures should be isolated per batch.
- Partial parsing failures must not crash the system.
- Services should be restartable independently in local development.

### Performance
- MVP should handle medium-sized log archives appropriate for local investigation.
- Upload-to-query latency should be short enough for interactive usage after ingestion completes.

### Security
- Limit AI tools to read-only investigation actions in MVP.
- Sanitize uploaded filenames and extracted archive paths.
- Restrict filesystem access during upload extraction.
- Avoid exposing arbitrary shell or network execution through the agent.

### Usability
- Setup should require a single local Docker Compose workflow.
- Dashboards should work out of the box.
- AI output should be readable by engineers without prompt engineering.

---

## 8. Product Scope and MVP Boundaries

### In Scope for MVP
- Local deployment with Docker Compose
- Upload API for zipped logs
- Parsing and normalization pipeline
- Loki ingestion
- Prometheus metric generation
- Grafana dashboard provisioning
- Document and repository indexing into Qdrant
- AI incident investigation agent with approved tools
- Structured incident report generation

### Out of Scope for MVP
- Kubernetes-native collection agents
- GitHub OAuth or live repository sync
- Role-based access control
- Multi-user workspaces
- Automatic alerting or anomaly detection triggering investigations
- Automated remediation actions

---

## 9. Assumptions

- Users can provide log archives manually for MVP.
- Repository and documentation sources are available locally or through mounted volumes.
- Incident investigation is retrospective rather than real-time in the initial release.
- Derived metrics from logs are sufficient for demonstrating observability value before adding native application instrumentation.
- Initial users are technical and comfortable using Grafana and API-driven workflows.
- Users supply their own API keys for their chosen LLM provider (OpenAI, OpenRouter, etc.); the platform does not bundle or mandate a single provider.

---

## 10. Dependencies

### Core Stack
- Python
- FastAPI
- Grafana
- Loki
- Prometheus
- Qdrant
- Configurable LLM provider (OpenAI, OpenRouter, or OpenAI-compatible API)
- LangGraph (or equivalent agent framework)
- Docker
- Docker Compose

### Internal Dependencies
- Log parser module before Loki ingestion
- Metrics generator before dashboard usefulness
- Knowledge ingestion before meaningful AI investigations
- Tooling contracts before reliable agent orchestration

---

## 11. Risks and Mitigations

### Risk: Inconsistent log formats reduce parsing accuracy
Mitigation: Use a canonical schema, layered format detection, fallback raw ingestion, and parsing summaries.

### Risk: Derived metrics from logs may be noisy or incomplete
Mitigation: Start with a minimal metric set and clearly mark metrics that rely on optional fields such as latency.

### Risk: AI agent may produce plausible but weak conclusions
Mitigation: Require structured outputs, source-backed evidence, and explicit uncertainty when confidence is low.

### Risk: Prompt injection through documentation or repository text
Mitigation: Treat retrieved content as untrusted data, validate tool use, and isolate system instructions.

### Risk: Local setup complexity slows adoption
Mitigation: Provide a single Compose-based developer workflow and provision dashboards automatically.

### Risk: Single LLM provider lock-in or availability
Mitigation: Design the AI layer around a configurable, OpenAI-compatible client (base URL + API key). Support OpenRouter and other gateways so users can choose models and providers without code changes.

---

## 12. Milestones

### Phase 1: Log Ingestion Foundation
- Build upload API
- Support archive extraction
- Parse common log formats
- Push normalized logs to Loki

### Phase 2: Observability Layer
- Derive metrics from logs
- Expose metrics to Prometheus
- Provision Grafana dashboards

### Phase 3: Knowledge Layer
- Ingest docs and runbooks
- Ingest repository code
- Generate embeddings and store in Qdrant

### Phase 4: AI Investigation
- Implement configurable LLM client (OpenAI-compatible; support OpenAI and OpenRouter via config)
- Implement tool interfaces
- Build LangGraph-based investigation flow
- Generate structured incident reports

### Phase 5: Incident Analysis Enhancements
- Improve anomaly analysis
- Expand report quality
- Prepare for future automated incident detection

---

## 13. Acceptance Criteria for MVP Release

The MVP is complete when:
- Users can upload zipped logs successfully.
- Parsed logs are visible and queryable in Loki/Grafana.
- Derived metrics are generated and shown on dashboards.
- Documentation and repository content can be indexed and retrieved.
- The AI agent can answer at least one end-to-end incident question using tools.
- The final report includes summary, likely cause, evidence, and recommended fix.
- The full stack runs locally via Docker Compose.

---

## 14. Future Opportunities

- Kubernetes log ingestion
- GitHub repository integration
- Automated incident detection
- AI-generated remediation guidance
- Alert-driven investigation workflows
- Feedback loops for report quality and investigation accuracy

---

## 15. Open Questions

- What is the maximum supported archive size for MVP uploads?
- Should repository indexing be manual, mounted, or Git-driven in the first release?
- Should incident reports be stored for later review and comparison?
- Should the AI agent expose confidence or evidence scoring in the MVP?
- What level of user authentication is required before moving beyond local-only usage?
- Which OpenRouter (or other gateway) models should be documented as recommended for incident investigation?
