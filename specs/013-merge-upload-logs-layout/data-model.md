# Data Model: 013 Merge Upload Logs and Layout

Entities and changes relevant to this feature. Existing sessions and reports models are unchanged.

## Session upload summary (extended)

**Entity**: Last upload result per session (already exists); this feature adds one attribute.

| Attribute            | Type         | Constraints | Notes |
|----------------------|--------------|-------------|--------|
| session_id           | TEXT         | PK, FK → sessions | Unchanged |
| status               | TEXT         | NOT NULL    | success \| partial \| failed |
| files_processed       | INTEGER      | NOT NULL    | Unchanged |
| files_skipped         | INTEGER      | NOT NULL    | Unchanged |
| lines_parsed         | INTEGER      | NOT NULL    | Unchanged |
| lines_rejected        | INTEGER      | NOT NULL    | Unchanged |
| error                 | TEXT         | nullable    | Unchanged |
| updated_at            | TEXT         | NOT NULL    | Unchanged |
| **uploaded_file_name** | TEXT       | nullable    | **New.** Original filename of the uploaded archive (e.g. "logs.zip"). Set on upsert; NULL for rows created before this feature. |

**Lifecycle**: One row per session; upserted on each upload. New column added by migration; existing rows have `uploaded_file_name = NULL`.

**Validation**: Store the filename as provided by the client (sanitized for display only; path segments stripped). Length limit acceptable per existing API constraints (e.g. reasonable max filename length).

## Frontend (no new persisted entities)

- **Latest upload summary (display)**: Same as API response — status, counts, `uploaded_file_name` (optional). No new client-side persistence; file name comes from GET upload-summary / POST upload response.
- **Report generation gate**: Derived from upload-summary query result (200 + status success/partial) plus in-tab last upload result; not a separate stored entity.
