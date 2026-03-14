<!--
Sync Impact Report
==================
Version change: (none) → 1.0.0 (initial ratification)
Modified principles: N/A (all new)
Added sections: Core Principles (5), Additional Constraints, Development Workflow, Governance
Removed sections: None
Templates:
  - .specify/templates/plan-template.md ✅ (Constitution Check gate already references constitution)
  - .specify/templates/spec-template.md ✅ (scope/requirements align; no mandatory section changes)
  - .specify/templates/tasks-template.md ✅ (task categorization supports principle-driven phases)
  - .specify/templates/commands/*.md: N/A (directory does not exist; .cursor/commands/*.md reviewed, no updates required)
  - .specify/templates/checklist-template.md ✅ (no constitution-specific references; no change needed)
Follow-up TODOs: None. All placeholders filled.
-->

# LogPilot Constitution

## Core Principles

### I. Local-First & Data Ownership

The platform MUST be deployable and operable locally (e.g., Docker Compose). Logs and derived
data stay under user control; no mandatory cloud or third-party data egress for core flows.

**Rationale**: Aligns with the PRD's "local-first DevOps platform" and user trust for incident data.

### II. Observability-First

Logs, metrics, and dashboards are first-class. Logs MUST be parsed, normalized, and queryable
(e.g., via Loki); metrics MUST be derived from logs and exposed (e.g., Prometheus); dashboards
MUST be provisioned for uploaded data so users can inspect system health without manual setup.

**Rationale**: Core value is moving from raw logs to searchable observability and visual trends.

### III. Evidence-Backed AI (NON-NEGOTIABLE)

The AI agent MUST use only approved tools (query_logs, query_metrics, search_docs, search_repo,
generate_incident_report). Output MUST be structured (Incident Summary, Possible Root Cause,
Supporting Evidence, Recommended Fix) and MUST cite evidence from logs, metrics, or knowledge
sources. The agent MUST NOT perform production remediation or arbitrary execution.

**Rationale**: Safety and trust; PRD guardrails require tool-based reasoning and auditability.

### IV. Independently Testable User Stories

Features MUST be specified as user stories with acceptance criteria and priorities (P1, P2, P3).
Each story MUST be implementable and testable independently; implementation plans and task lists
MUST reflect this so that incremental delivery and parallel work remain viable.

**Rationale**: Aligns with spec/plan/tasks workflow and MVP-first delivery.

### V. Simplicity & Scope Discipline

MVP scope is bounded by the PRD; additions MUST be justified. Prefer simple, typed Python and
clean architecture; avoid enterprise creep (no multi-tenant, full RBAC, SSO, or broad SIEM in
MVP). Complexity that conflicts with these constraints MUST be documented in the plan's
Complexity Tracking table with rationale and rejected alternatives.

**Rationale**: YAGNI; PRD non-goals and NFRs explicitly limit scope.

## Additional Constraints

- **Technology**: Python (typed), Loki for log storage, Prometheus for metrics, Grafana for
  dashboards, Qdrant for vector search. LLM provider MUST be configurable (OpenAI-compatible
  API, environment or configuration; no hardcoded vendor).
- **Security**: AI tools are read-only in MVP; sanitize uploads and extracted paths; restrict
  filesystem access during extraction; no arbitrary shell or network execution via the agent.
- **Performance**: Target medium-sized log archives and interactive upload-to-query latency;
  partial or batch failures MUST NOT crash the system.

## Development Workflow

Feature work follows **spec → plan → tasks**. Every implementation plan MUST pass the
Constitution Check (see plan template) before Phase 0 research and after Phase 1 design. Code
reviews and PRs MUST verify compliance with this constitution. Use `docs/PRD.md` and feature
specs under `specs/` for requirements; use the feature's `quickstart.md` when present for
validation and runtime development guidance.

## Governance

This constitution supersedes ad-hoc practices. Amendments require a version bump (semantic:
MAJOR = backward-incompatible principle changes, MINOR = new principle or section, PATCH =
clarifications), documentation of the change, and update of dependent templates. All PRs and
reviews MUST verify compliance. Complexity that conflicts with principles MUST be justified in
the plan's Complexity Tracking table. For runtime development guidance, use `docs/PRD.md`, the
feature's `spec.md`, and `quickstart.md` when available.

**Version**: 1.0.0 | **Ratified**: 2025-03-13 | **Last Amended**: 2025-03-13
