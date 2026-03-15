# Research: Single-Screen Layout, Pagination, and Copy Cleanup

**Branch**: 007-layout-single-screen-cleanup  
**Date**: 2026-03-15  

Resolves: charts library for upload/processing summary, layout approach for right-side space, and pagination implementation pattern (frontend vs backend).

---

## 1. Charts library for upload/processing summary

**Decision**: Use **Recharts** for the upload/processing summary (files processed, skipped, lines parsed, rejected, parsed coverage). Add `recharts` to frontend dependencies.

**Rationale**: Recharts is React-first, tree-shakeable, and fits the existing stack (TypeScript, React 18). It supports bar charts, pie/donut, and simple progress indicators. For the summary we need: (1) parsed vs rejected (e.g. bar or donut), (2) coverage % (e.g. progress bar or small gauge). No NEEDS CLARIFICATION; spec allows "any suitable charts library"; Recharts is a common choice for React dashboards.

**Alternatives considered**:
- **Chart.js + react-chartjs-2**: Heavier and imperative; Recharts is declarative and aligns with React.
- **Nivo**: Rich but larger bundle; Recharts is sufficient for a few summary charts.
- **Custom SVG/CSS**: More work to maintain; a library keeps implementation consistent and accessible.

**Integration**: Render the existing `UploadResult` (files_processed, files_skipped, lines_parsed, lines_rejected) and derived coverage % in a small chart group (e.g. `BarChart` for counts + `ProgressBar` or radial for coverage). Keep text summary available for accessibility; charts are visual enhancement per FR-012.

---

## 2. Layout: use right-side space (horizontal / multi-column)

**Decision**: Use **CSS Grid** for the main session view content area so that Upload logs, Logs & metrics, and Reports can be arranged in a grid (e.g. two columns on wide viewports). Sidebar stays left; main content uses `grid-template-columns` (e.g. `1fr 1fr` or `minmax(0, 1fr) minmax(0, 1fr)`) to place some sections to the right and achieve single-screen fit at ≥1280×720.

**Rationale**: Spec requires "moving some sections to the right" and "horizontal or multi-column arrangement". Grid allows responsive columns without extra JS; Tailwind supports `grid-cols-2`, `lg:grid-cols-2`, etc. No collapsible sections; if content still overflows after rearrangement, scrolling is acceptable (per spec).

**Alternatives considered**:
- **Flexbox only**: Works but grid gives clearer multi-column control for 2–3 blocks.
- **Multiple rows with flex wrap**: Equivalent; grid is explicit and matches "sections to the right" mental model.

**Integration**: In the home/session view, wrap the three main sections (Upload logs, Logs & metrics, Reports) in a grid container. Use breakpoints so that at typical desktop width the layout is two (or three) columns; on narrow viewports fall back to one column and allow scroll.

---

## 3. Pagination: Load more + optional Previous (sessions and KB search)

**Decision**: Implement **frontend-driven pagination** with "Load more" and optional "Previous" (or back-to-start):

- **Sessions list**: Keep using `getSessions()` (full list). Slice in UI into batches of size `batchSize` (10/20/50). Show first batch; "Load more" appends next batch; "Previous" (or "Back to start") shows previous batch or resets to first batch. No backend API change required for MVP; if backend later adds `?limit=&offset=` (or cursor), frontend can switch to server-driven pagination.
- **KB search**: Existing API likely returns a list; add `limit` (and optionally `offset`) to the search request if the backend supports it; otherwise paginate in frontend over the returned list with the same batch-size control. Spec requires same pattern for both (Load more + optional Previous); default batch size 10, user choice 10/20/50.

**Rationale**: Spec: "Same pattern for both — Load more with optional Previous or back-to-start". Frontend pagination over full list is acceptable for medium-sized lists and avoids backend changes in the first slice; backend can add params later for scale.

**Alternatives considered**:
- **Backend-only pagination from day one**: Requires API changes and more coordination; frontend pagination delivers the UX quickly.
- **Infinite scroll**: Spec explicitly rejects infinite scroll for these lists.

**Integration**: SessionList: state for `visibleCount` or `pageStart`/`pageEnd`, batch size from dropdown (10/20/50), "Load more" and "Previous" buttons. KnowledgeSearch: same pattern on the result list; if the search API supports limit/offset, pass batch size as limit and track offset for Load more.

---

## 4. Top bar: clickable LogPilot + app icon (Lucide)

**Decision**: In AppLayout, render the application name (e.g. "LogPilot") as a **link** (e.g. `<Link to="/">`) so it navigates to home. Add an **icon** from lucide-react next to it (e.g. `ScrollText` or `FileText` for logs). Spec allows "e.g. logs-related"; implementation picks one and keeps it consistent.

**Rationale**: FR-008 and FR-009; spec and clarifications already state LogPilot in top bar returns to home and an app icon (Lucide, logs-related) is shown. No research unknown.

**Integration**: Replace or wrap the top-bar "LogPilot" text with `<Link to="/">` and prepend or append a Lucide icon (e.g. `<ScrollText size={20} />`). Ensure aria-label for accessibility (e.g. "LogPilot – home").

---

## 5. Back to Home inside knowledge space only

**Decision**: Remove "Back to Home" from the **top nav** when on the knowledge page. Render "Back to Home" (or equivalent) **inside** the knowledge page content (e.g. above or beside the Knowledge base and Search knowledge base sections). Use React Router `<Link to="/">` or similar.

**Rationale**: FR-005 and User Story 3; spec says the control must be within the knowledge space content area, not in the global top navigation.

**Integration**: In KnowledgePage, add a prominent link/button at the top of the main content. Ensure AppLayout does not show a global "Back to Home" in the navbar on `/knowledge` (or remove it from navbar entirely and rely on this in-content link when on `/knowledge`).

---

## 6. Copy and icon deduplication

**Decision**: (1) **Copy**: Remove duplicate headings/body text (e.g. single "Knowledge base" heading and one short description; no identical repeated phrase). (2) **Icons**: Use **distinct** Lucide icons for upload (e.g. `Upload`) vs generate report (e.g. `FileOutput` or `Sparkles`); avoid reusing the same icon for semantically different actions.

**Rationale**: FR-006, FR-007; spec and clarifications. No NEEDS CLARIFICATION.

**Integration**: Audit KnowledgePage and session view for repeated headings/descriptions; consolidate. Audit buttons/links for icon semantics; assign distinct icons to Upload logs vs Generate report and any other actions that currently share an icon.
