# Contract: Upload and Upload Summary API

Scope: 013 merge upload logs layout — addition of `uploaded_file_name` and `updated_at` (upload time) to responses; behavior unchanged otherwise.

## GET /sessions/{session_id}/upload-summary

**Purpose**: Return the last upload result for the session (for display after refresh or session switch).

**Response**: 200 OK

| Field               | Type    | Required | Notes |
|---------------------|---------|----------|--------|
| status              | string  | yes      | `success` \| `partial` \| `failed` |
| files_processed     | number  | yes      | |
| files_skipped       | number  | yes      | |
| lines_parsed       | number  | yes      | |
| lines_rejected     | number  | yes      | |
| session_id         | string  | yes      | |
| error              | string \| null | yes | Error message when status is `failed` |
| **uploaded_file_name** | string \| null | yes | **New.** Original filename of the uploaded archive (e.g. `"logs.zip"`). Null for summaries created before this field existed. |
| **updated_at**         | string         | yes | When the upload was stored (e.g. ISO 8601). Used by the client to display "when the upload occurred" (date/time or relative time). |

**Errors**: 404 if session not found or session has never had an upload.

---

## POST /sessions/{session_id}/logs/upload

**Purpose**: Upload a compressed log archive for the session. Returns upload result including the stored filename.

**Request**: `multipart/form-data` with field `file` (`.zip`).

**Response**: 200 OK — same shape as GET upload-summary (including `uploaded_file_name` and `updated_at`). Server stores the client-provided filename and returns it with `updated_at` in the response and in subsequent GET upload-summary for that session.

**Errors**: 404 session not found; 413 archive too large; 400 invalid file (e.g. not .zip) or validation failure.

**New behavior**: Response MUST include `uploaded_file_name` set to the original filename of the uploaded file (or null if not provided) and `updated_at` (when the summary was stored). Both returned so GET upload-summary provides them for display (file name and "when the upload occurred").
