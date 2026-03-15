# Quickstart: Log Investigation Frontend

**Branch**: `002-frontend-implementation`  
**Date**: 2026-03-14  

Minimal steps to run the frontend locally and validate it against the backend. Use for development and manual testing.

---

## Prerequisites

- **Backend and infrastructure** running (see [001-log-investigation-mvp quickstart](../001-log-investigation-mvp/quickstart.md)): Docker Compose (Loki, Prometheus, Grafana, Qdrant), backend API at `http://localhost:8000`.
- **Node.js** 18+ and npm/pnpm/yarn.

---

## 1. Install frontend dependencies

From the repository root:

```bash
cd frontend && npm install
```

(Or `pnpm install` / `yarn` if the project uses them.)

---

## 2. Configure environment

Create `frontend/.env` or `frontend/.env.local` with:

```bash
# Backend API base URL (no trailing slash)
VITE_API_BASE=http://localhost:8000

# Grafana base URL for "Open metrics/dashboard" link (optional; default http://localhost:3000)
VITE_GRAFANA_URL=http://localhost:3000
```

For dev, Vite will proxy API requests to the backend if configured in `vite.config.ts` (e.g. proxy `/api` → `http://localhost:8000`) so the SPA can use relative paths; otherwise use full `VITE_API_BASE` for fetch calls.

---

## 3. Run the frontend dev server

From `frontend/`:

```bash
npm run dev
```

Open the URL shown (e.g. `http://localhost:5173`). The app will use the configured backend; ensure the backend is running so that session list, upload, log search, reports, and knowledge flows work.

---

## 4. Validate main flows

1. **Sessions**: Create a session, give it a name/link, list sessions, select one as current, edit name/link.
2. **Upload**: Select a session, upload a `.zip` log archive, confirm success and summary (files processed, lines parsed/rejected/skipped).
3. **Log search**: With a session that has logs, set time range and optional filters (service, level), run search, confirm log lines and metadata.
4. **Metrics link**: Click "Open metrics/dashboard"; Grafana should open in a new tab with session context if applicable.
5. **Knowledge**: Trigger ingest, poll status until idle; run a search and confirm chunks with snippets and source paths.
6. **Reports**: Enter an incident question, trigger report generation, poll until content appears, view report, export as Markdown or PDF.

---

## 5. Build for production

From `frontend/`:

```bash
npm run build
```

Output is in `frontend/dist/`. Serve with any static host; set `VITE_API_BASE` and `VITE_GRAFANA_URL` at build time so the app points to the correct backend and Grafana.

---

## 6. Troubleshooting

- **CORS errors**: Backend already allows `*`; if using a different origin, ensure backend CORS config includes it.
- **404 on API calls**: Confirm `VITE_API_BASE` (or proxy target) matches the running backend URL and path (e.g. `/sessions` not `/api/sessions` unless backend is mounted under `/api`).
- **Report export 409**: Report content is still empty; keep polling GET report until `content` is non-empty, then retry export.
- **Grafana link**: If Grafana runs on another host/port, set `VITE_GRAFANA_URL` and ensure the link includes session context (e.g. query param) as documented in contracts.
