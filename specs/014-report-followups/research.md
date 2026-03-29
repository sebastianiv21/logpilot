# Research: Report Follow-Up Improvements

**Branch**: `014-report-followups`  
**Date**: 2026-03-29  
**Goal**: Resolve implementation choices for question-aware report history, coding-agent fix prompt generation, Markdown copy behavior, and reliable PDF export.

---

## 1. Persisting incident questions for report history

**Decision**: Persist the full incident question string with each report record in SQLite, expose a short preview in the report-list response, and expose the full stored question in the report-detail response.

**Rationale**: The current report record stores only `id`, `session_id`, `content`, and `created_at`, so report history has no investigation context. Storing the original question as report metadata is the smallest durable addition that satisfies history preview, on-demand access to the full question, and consistency across refreshes and exports. A preview should be derived from the stored question rather than entered separately so there is only one source of truth.

**Alternatives considered**:
- Derive question text from report Markdown content only: rejected because history loads before detail content and parsing report prose would be fragile.
- Store preview text only: rejected because the spec requires access to the full question set on demand.
- Keep question only in frontend state: rejected because history must remain accurate after reloads and across sessions.

---

## 2. Report contract for the new coding-agent fix prompt

**Decision**: Extend the report-generation prompt and section contract so the agent emits a dedicated `## Coding agent fix prompt` section as part of the full report, and keep it out of the report history list.

**Rationale**: The spec requires a distinct handoff prompt for a coding agent, not just a general recommendation. Adding a dedicated section keeps this content explicit, exportable, and testable, while preserving the lightweight history list. The backend prompt and `REPORT_SECTIONS` constant are the right source of truth because they already define the required report structure.

**Alternatives considered**:
- Fold the coding-agent handoff into `Recommended Fix`: rejected because the spec calls for a dedicated prompt section and a separate handoff audience.
- Show the prompt in report history too: rejected during clarification because it would overload the list and reduce scanability.
- Generate the prompt client-side from report content: rejected because the agent should author the canonical report content once, server-side.

---

## 3. Clipboard behavior for the viewport copy button

**Decision**: Copy the report’s Markdown content directly from the fetched report detail and mirror the compact session-ID copy interaction pattern for button size, placement, and toast feedback.

**Rationale**: The spec and clarification require Markdown on the clipboard. The report detail already exposes Markdown content, so copying that exact string avoids a second transformation layer and keeps copy/export behavior aligned. Reusing the existing session-ID control pattern lowers UI complexity and keeps the new affordance familiar.

**Alternatives considered**:
- Copy rendered HTML/rich text: rejected because it adds browser-specific clipboard complexity and drifts from the clarified Markdown requirement.
- Copy stripped plain text: rejected because it would lose headings, lists, and fenced code blocks that users expect to paste into tickets or coding tools.
- Add a separate backend copy endpoint: rejected because the frontend already has the necessary report content.

---

## 4. PDF export reliability strategy

**Decision**: Keep server-side PDF generation with ReportLab, but harden the Markdown-to-flowables pipeline around the actual report shapes this feature adds: long incident questions, an extra report section, and mixed prose/code/list blocks. Add focused backend tests for representative report fixtures and ensure export failures map to a stable user-facing error.

**Rationale**: The exporter already uses ReportLab and list-aware HTML parsing. The reliability issue is more likely triggered by specific Markdown content shapes than by a missing export stack. Strengthening the current pipeline is lower risk than swapping libraries, and fixture-based tests will catch regressions around long lines, new headings, ordered lists, code blocks, and question text.

**Alternatives considered**:
- Replace ReportLab with another PDF renderer: rejected as unnecessary scope for this feature.
- Generate PDFs in the browser: rejected because export already belongs to the backend and should stay consistent across clients.
- Ignore unsupported content and silently degrade: rejected because the spec requires readable output or a clear failure.

---

## 5. API response shape for history preview vs full question

**Decision**: Extend `GET /sessions/{session_id}/reports` to return preview-oriented metadata for each history row, and extend `GET /sessions/{session_id}/reports/{report_id}` to return the full stored incident question along with report content.

**Rationale**: The list and detail views have different information-density needs. A preview field in the list keeps the UI scannable; the detail response can carry the full question for on-demand display without forcing the list to overfetch or overrender. This matches the clarified UX requirement cleanly.

**Alternatives considered**:
- Return the full question in list responses only and let the UI truncate: acceptable but less explicit, and it couples scanability rules to every consumer.
- Add a dedicated history metadata endpoint: rejected because the current reports API already covers the needed surfaces.

---

## 6. Testing strategy

**Decision**: Add both frontend and backend coverage for the new report flow. Frontend tests should cover question preview rendering, the history/detail boundary, and Markdown clipboard success/failure feedback. Backend tests should cover schema migration for the new report-question field and PDF export success/failure for representative report content.

**Rationale**: The codebase currently has almost no report-specific test coverage. This feature spans persistence, API, UI rendering, clipboard UX, and export behavior, so relying on manual validation alone would leave the PDF fix and history metadata easy to regress.

**Alternatives considered**:
- Manual testing only: rejected because PDF and report-history regressions are subtle and repeatable fixtures are inexpensive.
- Backend-only tests: rejected because the copy button and history preview are primarily frontend behavior.
