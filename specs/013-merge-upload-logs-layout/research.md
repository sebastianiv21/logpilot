# Research: 013 Merge Upload Logs and Layout

Resolves technical decisions for the merge-upload-logs-layout feature. No NEEDS CLARIFICATION remained after spec clarification; this document records implementation choices and alternatives.

## 1. Storing and returning uploaded file name

**Decision**: Add `uploaded_file_name` (TEXT, nullable) to `session_upload_summary` and to the upload API request/response and GET upload-summary response. Backend persists the original filename from the multipart upload and returns it in both POST upload and GET upload-summary.

**Rationale**: Spec (FR-006, clarifications) requires file name to be available after refresh or session switch; client-only storage would not satisfy that. Storing on the server keeps a single source of truth and aligns with existing upload-summary persistence.

**Alternatives considered**:
- Client-only storage (e.g. with last upload result in context): Rejected because spec explicitly chose backend storage for availability after refresh/switch.
- Show file name only for the current page session: Rejected per clarification (Option A: backend stores and returns).

## 2. Deriving "session has upload" for report generation gate

**Decision**: Use the existing GET upload-summary response: if the query returns 200 with `status` in `['success', 'partial']`, treat the session as having an upload and enable report generation. If the query returns 404 (no summary) or 200 with `status === 'failed'`, keep report generation unavailable. Combine with client-side last-upload result so that immediately after a successful/partial upload in the same tab, reports become available without waiting for a refetch.

**Rationale**: Avoids a new backend endpoint; reuses existing upload-summary contract. Success and partial both indicate logs were ingested; failed does not. Frontend already fetches upload summary for the current session for the summary block, so the same data can drive the report gate.

**Alternatives considered**:
- New GET /sessions/:id/has-upload: Rejected as unnecessary; upload-summary presence and status are sufficient.
- Rely only on client-side sessionIdsWithLogs: Rejected because it does not persist across refresh (spec requires report gate to work after refresh).

## 3. Report generation "unavailable" UX

**Decision**: Implement as disabled controls with a short indication (e.g. "Upload logs to generate reports" or tooltip) rather than hiding the Reports section. Section remains visible so layout and two-column structure stay consistent; only the actionable report generation is gated.

**Rationale**: Spec (FR-008) allows "disabled or hidden with clear indication"; disabled + message is more discoverable and keeps the layout stable. Hiding the whole section would change layout when toggling.

**Alternatives considered**:
- Hide entire Reports section until upload: Would collapse to single column when no upload, contradicting two-column layout requirement.
- Disable without message: Rejected; spec requires "clear indication."

## 4. Loading state for upload summary area

**Decision**: Show a loading indicator (e.g. spinner or skeleton) in the latest-upload-summary area while the upload-summary query is loading (e.g. `isLoading` or `isFetching` and no data yet). When there is no summary (404), show an empty/neutral state, not a perpetual loader.

**Rationale**: Matches FR-007 and clarification: users see that data is loading. Distinguishing "loading" vs "no upload yet" avoids confusion for new sessions.

## 5. Migration for new column

**Decision**: Add `uploaded_file_name` via schema migration: extend `session_upload_summary` with a new column (e.g. `ALTER TABLE` or recreate table in init if acceptable for the project). Existing rows have `uploaded_file_name` NULL; new uploads set it. API returns null when not set (e.g. legacy summaries).

**Rationale**: Backward compatible; no need to backfill old data. Frontend already handles optional file name (show when present).

**Alternatives considered**:
- Backfill from existing data: Not possible; previous uploads did not store filename.
- New table for "last upload metadata": Rejected; one extra column is simpler than a new table.

## 6. Displaying when the upload occurred

**Decision**: Use the existing `updated_at` column on `session_upload_summary` (already set on upsert). API returns it in GET upload-summary and POST upload response (e.g. as ISO 8601 string or epoch). Frontend displays it as date/time or relative time (e.g. "2 hours ago"); format is an implementation choice (e.g. date-fns formatDistanceToNow or format()).

**Rationale**: Spec (FR-002, clarification) requires showing when the upload occurred. No new backend column; `updated_at` is the natural source. Frontend can show absolute or relative time per UX preference.

**Alternatives considered**:
- New column `uploaded_at` distinct from `updated_at`: Rejected; semantics are the same for "last upload time."
- Server-computed relative string: Rejected; client can format based on user locale and preference.
