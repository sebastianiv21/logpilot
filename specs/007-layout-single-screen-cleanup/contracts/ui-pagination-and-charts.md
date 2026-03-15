# UI Contract: Pagination and Upload Summary Charts

**Branch**: 007-layout-single-screen-cleanup  
**Date**: 2026-03-15  

Describes the UI behavior and props for paginated lists and the upload/processing summary visualization. No formal API; this is a contract for frontend components.

---

## 1. Paginated list (sessions list and KB search)

**Components**: SessionList, KnowledgeSearch (or equivalent list that displays sessions / search results).

**Behavior**:
- List is divided into batches of size **10** (fixed; no user control).
- First batch is shown initially.
- **Load more**: Button or control that appends the next batch (or requests next page if backend supports it). Disabled or hidden when no more items.
- **Previous** (or back-to-start): Optional control to show the previous batch or jump to first batch. Hidden or disabled when on first batch.

**Props (advisory)**:
- Items: from existing data (sessions array or search results array); slicing or paging is component-internal; batch size is constant 10.

**Accessibility**: Buttons have clear labels (e.g. "Load more sessions", "Previous"); batch size control has aria-label. List region has appropriate role and semantics.

---

## 2. Upload/processing summary (charts)

**Component**: Renders after upload success or partial; receives `UploadResult`.

**Input**: `UploadResult` with at least:
- `status`: 'success' | 'failed' | 'partial'
- `files_processed`, `files_skipped`, `lines_parsed`, `lines_rejected`: numbers
- When status is success or partial: display visual summary. When failed: show error message (no charts required).

**Behavior**:
- Present **files** counts (processed vs skipped) in visual form (e.g. bar chart or donut).
- Present **lines** counts (parsed vs rejected) in visual form (e.g. bar chart or donut).
- Present **parsed coverage** (derived: lines_parsed / (lines_parsed + lines_rejected) as %) in visual form (e.g. progress bar or radial).
- Charts library: Recharts (per research.md). Keep a short text summary or ensure chart labels/aria for accessibility.

**Props (advisory)**:
- `result: UploadResult | null` — when non-null and status !== 'failed', show charts.
- Optional `className` or layout props for grid placement.

**Accessibility**: Charts have titles/labels; consider aria-label or table fallback for key values.
