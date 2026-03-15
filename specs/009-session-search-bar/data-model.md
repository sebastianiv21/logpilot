# Data Model: Session Search Bar

**Branch**: 009-session-search-bar  
**Date**: 2026-03-15  
**Source**: Feature spec; UI/ephemeral state only. No new backend entities or persistence.

---

## 1. Session (unchanged)

**Source**: Existing `Session` from API and `frontend/src/lib/schemas.ts`: id, name, external_link, created_at, updated_at. No schema or API changes. Search matches against name, id, and external_link (case-insensitive substring after trim).

---

## 2. Search query (ephemeral UI state)

- **Raw input**: String value of the search input (what the user types). Not persisted.
- **Trimmed query**: `rawInput.trim()`. If empty, treat as "no filter" (show full list).
- **Debounced query**: Value used for filtering; updates 150–300 ms (e.g. 200 ms) after the user stops typing. Derived from trimmed raw input via a debounce hook (e.g. `useDebouncedValue(trimmedQuery, 200)`).

Validation: Trim before applying; empty trimmed string → show all sessions. No persistence; state lives in component (or wrapper) that owns the search input.

---

## 3. Filtered session list (derived)

- **Input**: List of sessions from existing API (`useSessionsList().data?.sessions`) and debounced search query.
- **Rule**: Session is included if the trimmed, debounced query is empty, OR if (query as substring, case-insensitive) appears in at least one of: `session.name ?? ''`, `session.id`, `session.external_link ?? ''`.
- **Output**: Ordered list of sessions to render in the session list. Pagination (e.g. "Load more") applies to this filtered list, not the full list, so "visible count" is relative to filtered results.

No new API or storage. Derived in the component that renders the session list (or a wrapper that holds search state and passes filtered sessions to SessionList).

---

## 4. Empty state (display)

- **No sessions at all**: Existing behavior — "No sessions yet. Create one to get started." (no filter applied).
- **Sessions exist but none match filter**: Show a dedicated empty state message, e.g. "No sessions match your search", so the user knows the result is from the filter. Not a generic "no sessions" or loading state.

Display logic only; no new fields.

---

## 5. Live region content (a11y)

- **When filtered and matches exist**: Announce count, e.g. "3 sessions" (or "1 session").
- **When filtered and no matches**: Announce "No sessions match your search" (or equivalent).
- **When filter is empty**: Optional — can announce total count or omit to avoid noise; spec requires announcement when filtered list is empty and when result count is exposed.

Content is derived from filtered list length and query (empty vs non-empty). Implemented via a visually hidden or off-screen element with `aria-live="polite"` and `aria-atomic="true"`, text updated when debounced filter result changes.

---

No new backend entities. Backend Session schema and sessions API unchanged.
