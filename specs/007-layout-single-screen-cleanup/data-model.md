# Data Model: Single-Screen Layout, Pagination, and Copy Cleanup

**Branch**: 007-layout-single-screen-cleanup  
**Date**: 2026-03-15  
**Source**: Feature spec; entities are mostly UI/state. Backend may add optional pagination params (see contracts).

---

## 1. Session list (paginated, client state)

**Source**: Existing `Session[]` from GET /sessions; no backend schema change required for frontend pagination.

- **Sessions**: Array of `Session` (id, name, created_at, external_link, etc.). Fetched in full (or via optional limit/offset if backend adds it).
- **Batch size**: Fixed at 10; no user-adjustable control.
- **Visible range**: Client state (e.g. `visibleCount`) for "Load more" and "Previous". First batch = first 10 items; Load more adds 10; Previous goes back one batch.
- **Validation**: Visible range ≥ 0 and ≤ length of sessions list.

No new backend entities. If backend later adds pagination, request params could be `limit` and `offset` (or `cursor`); response could include `sessions`, `total`, `has_more`.

---

## 2. Search result set (KB search, paginated)

**Source**: Existing KB search API (e.g. returns a list of results). Same pagination pattern as sessions.

- **Results**: Array of search result items (content, score, metadata, etc.). Either full response paginated in UI, or API supports `limit`/`offset` and returns a page.
- **Batch size**: Fixed at 10; same as sessions list (no user control).
- **Visible range**: Same pattern as sessions—first batch, Load more, optional Previous.
- **Validation**: Visible range within result length.

No new backend entities. If the search API already has a `limit` (and optionally `offset`) parameter, use it and request next page on Load more; otherwise paginate in frontend over the returned list.

---

## 3. Upload/processing summary (for charts)

**Source**: Existing `UploadResult` from POST .../logs/upload (status, files_processed, files_skipped, lines_parsed, lines_rejected, error).

- **Fields used for visualization**:
  - `files_processed`, `files_skipped` — counts for bar or donut (e.g. "Processed" vs "Skipped").
  - `lines_parsed`, `lines_rejected` — counts for bar or donut (e.g. "Parsed" vs "Rejected").
  - **Parsed coverage**: derived as `lines_parsed / (lines_parsed + lines_rejected)` when denominator > 0; else 0 or N/A. Displayed as percentage (e.g. progress bar or radial).
- **State**: Shown after a successful or partial upload; no new persistence. Component receives `UploadResult` and passes it to the charts component.

No new backend fields. Validation: numbers ≥ 0; coverage in [0, 100] or N/A.

---

## 4. Knowledge space view state

- **Back to Home**: In-content link/button only (not in top nav). No new data; route is `/knowledge`, link targets `/`.
- **Copy/headings**: Single "Knowledge base" heading and one description; no duplicate subheading with identical text. Purely presentational.

---

## 5. Top bar (navigation and branding)

- **Application name**: Rendered as link to `/` (home). No new entity.
- **Application icon**: Lucide icon (e.g. ScrollText) next to or before the name. No new entity; choice is implementation constant.

---

## 6. Batch size (fixed)

- **Value**: 10 for both sessions list and KB search.
- **Scope**: No user control; fixed at 10 per product decision.

No persistence; constant in code.
