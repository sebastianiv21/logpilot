# API Contract: Optional pagination for sessions and KB search

**Branch**: 007-layout-single-screen-cleanup  
**Date**: 2026-03-15  

Backend **may** add optional query parameters to support server-side pagination. Frontend will work with or without these; if not present, frontend paginates over the full response.

---

## 1. GET /sessions (optional)

**Current**: Returns full list of sessions (array).

**Optional extension**:
- Query params: `limit` (number, default e.g. 50), `offset` (number, default 0).
- Response: Either unchanged `{ sessions: Session[] }` (frontend slices for pagination) or `{ sessions: Session[], total?: number, has_more?: boolean }` when backend supports pagination.

**Contract**: If backend adds `limit` and `offset`, frontend may send them and use the returned slice plus `total`/`has_more` for Load more and Previous. If not added, frontend uses full list and client-side batching only.

---

## 2. KB search (optional)

**Current**: Search endpoint returns a list of results (and may already accept a `limit` or similar).

**Optional extension**:
- Request: Ensure `limit` (and optionally `offset` or `cursor`) can be sent so that "Load more" requests the next page from the server.
- Response: Page of results plus optional `total` or `has_more`.

**Contract**: If the API supports limit/offset (or cursor), frontend uses it for Load more; otherwise frontend paginates over the full result list with the same batch size (10/20/50) and Load more / Previous pattern.
