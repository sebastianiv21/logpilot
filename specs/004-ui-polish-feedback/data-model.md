# Data Model: UI polish — icons, copy, loading cues, report-ready feedback

**Branch**: `004-ui-polish-feedback`  
**Date**: 2026-03-15  
**Source**: Feature spec. No new persistence or API schema; this document confirms no new entities and references existing UI state where relevant.

---

## 1. No new entities

This feature does not introduce new domain entities, API contracts, or stored data. It only changes:

- **Presentation**: Loading indicators, icons, and copy in the frontend.
- **Client-side feedback**: Toast and sound when a report transitions from generating to ready, using existing report and session data.

---

## 2. Existing state relied upon

- **Report** (existing): `id`, `session_id`, `content`, `created_at`. The moment `content` becomes non-empty is when “report ready” is triggered.
- **ReportGenerationContext** (existing): `generatingBySession: Record<string, string>` (sessionId → reportId). When polling finds content, the entry is removed; that transition is the trigger for notification.
- **Session** (existing): Session name or id may be used in the report-ready toast when multiple sessions have reports generating (per Clarifications).

No new fields or tables are added.
