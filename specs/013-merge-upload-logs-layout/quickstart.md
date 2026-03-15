# Quickstart: 013 Merge Upload Logs and Layout

Use this for local validation and development of the merge-upload-logs-layout feature.

## Prerequisites

- Backend and frontend runnable as per main project (Python 3.11+, Node 18+).
- Database with existing schema; migration adds `uploaded_file_name` to `session_upload_summary` (see data-model.md).

## Backend

1. **Migration**: Ensure `session_upload_summary` has column `uploaded_file_name` (TEXT, nullable). Apply via project migration or init path (e.g. `ALTER TABLE session_upload_summary ADD COLUMN uploaded_file_name TEXT`).
2. **Upload flow**: POST `/sessions/{id}/logs/upload` with a `.zip` file; response must include `uploaded_file_name` (the original filename) and `updated_at` (upload time).
3. **Summary**: GET `/sessions/{id}/upload-summary` returns last result including `uploaded_file_name` (null for legacy rows) and `updated_at`.

**Verify**:
- Create a session, POST upload with file `test.zip`; response has `uploaded_file_name: "test.zip"` and `updated_at` (e.g. ISO 8601).
- GET same session’s upload-summary; response has `uploaded_file_name: "test.zip"` and `updated_at`.

## Frontend

1. **Home layout**: Two-column grid: left = section "Logs & metrics" (upload + latest summary + metrics link), right = Reports (generate + list). Session title above. Responsive: stack on narrow viewports.
2. **Logs & metrics section**: Single heading "Logs & metrics"; contains file input, upload button, latest upload summary (with file name and when the upload occurred when present), and "Open in Grafana" (no helper text "Opens in a new tab; updates when you switch sessions.").
3. **Upload summary**: Show loading indicator (spinner/skeleton) while upload-summary query is loading; display file name and upload time (e.g. date/time or "2 hours ago") from API when present.
4. **Report gate**: Report generation (and list) disabled or hidden until current session has an upload (upload-summary 200 with status success/partial, or last upload in tab with success/partial). Show short message (e.g. "Upload logs to generate reports").

**Verify**:
- No session selected: upload and reports unavailable or neutral.
- Session selected, no upload: "Logs & metrics" shows upload UI; summary area empty or loading then empty; reports unavailable with message.
- After upload: summary shows status, file name, and when the upload occurred; reports become available.
- Refresh: summary (file name and upload time) from API; reports available if summary exists with success/partial.
- Metrics link: no "Opens in a new tab…" copy; button still opens Grafana in new tab.

## Acceptance checklist (from spec)

- [ ] One section "Logs & metrics" with upload, summary, and metrics link.
- [ ] Latest upload summary shows uploaded file name and when the upload occurred (when available from API).
- [ ] Two-column layout (Logs & metrics | Reports); responsive stack on small screens.
- [ ] Helper copy "Opens in a new tab; updates when you switch sessions." removed.
- [ ] Loading indicator in summary area while upload-summary is loading.
- [ ] Report generation unavailable until session has at least one (success/partial) upload; clear indication when unavailable.
