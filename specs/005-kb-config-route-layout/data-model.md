# Data Model: Knowledge base config route and layout

**Branch**: `005-kb-config-route-layout`  
**Date**: 2026-03-15  
**Source**: Feature spec. No new persistence or API schema; this document describes UI/routing state and existing API usage.

---

## 1. No new domain entities

This feature does not add new backend entities, tables, or API contracts. It adds:

- **Routes**: New path for the knowledge base page (e.g. `/knowledge`).
- **UI state**: Derived indicator state (red / yellow / green) from existing knowledge ingest status API.

---

## 2. Existing API used

**Knowledge ingest status** (existing):

- **Source**: `GET /knowledge/ingest/status`
- **Shape**: `{ status: 'running' | 'idle', last_result?: { chunks_ingested?, files_processed? } | null, error?: string | null }`
- **Usage**: Already used by `useKnowledgeIngest` and `KnowledgeIngest` / `KnowledgeSearch`. The new header control will use the same hook (or `useKnowledgeIngestStatus`) to drive the status indicator.

**Indicator state derivation** (client-side):

| API state | Indicator |
|-----------|-----------|
| `status === 'running'` | Yellow/ochre, pulsating |
| `status === 'idle'` and `last_result` and !`error` | Green |
| `status === 'idle'` and (!`last_result` or `error`) | Red (no/empty/failed) |

---

## 3. Client-side routing state

- **Route**: React Router path `/knowledge` (or chosen path) for the knowledge base page; `/` for home. No new global store required; layout reads current location to show active state and return link.
- **No session dependency**: KB is global; no session id is required to show the knowledge page or the indicator (status is app-wide).

No new fields or tables are added.
