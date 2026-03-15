# Research: Log Investigation Frontend

**Branch**: `002-frontend-implementation`  
**Date**: 2026-03-14  
**Goal**: Resolve technology choices for the frontend (framework, build, UI library). All NEEDS CLARIFICATION from Technical Context are resolved below.

---

## 1. Frontend stack (framework + build + UI)

**Decision**: **Vite + React + Tailwind CSS + DaisyUI + TanStack Query + Zod + React Hook Form + date-fns + Sonner**

- **Vite**: Build tool and dev server; minimal config, fast HMR and production builds.
- **React**: Component model and ecosystem for the highly interactive UI (sessions, upload, log search, report generation, export).
- **Tailwind CSS**: Utility-first CSS; small production bundle; themeable.
- **DaisyUI**: Tailwind plugin providing ready-made component classes (buttons, cards, forms, tables, modals, alert) that look good out of the box; lighter than a full component library (e.g. MUI).
- **TanStack Query**: Server state and data fetching (caching, deduplication, background refetch, polling). Used for all API-backed data: session list, report list, report detail (including polling until content is ready), knowledge ingest status, log query results.
- **Zod**: Schema validation for API responses and form input; TypeScript inference; use with TanStack Query and React Hook Form.
- **React Hook Form**: Form state with minimal re-renders; pairs with Zod via `@hookform/resolvers/zod` for validation.
- **date-fns**: Format `timestamp_ns` and `created_at` for display (log table, report list, session list); small and tree-shakeable.
- **Sonner**: Toasts for success/error/info feedback (upload complete, report ready, ingest failed). Styled with DaisyUI’s alert classes so toasts match the app theme (see §8).

**Rationale**: The app is almost entirely interactive (session list, upload, filters, log table, report trigger/poll, export). There is no content-site or SEO requirement, so a SPA is appropriate. Vite + React gives a single, fully interactive app that talks to the existing FastAPI backend. Tailwind + DaisyUI keeps styling consistent and reduces custom CSS. TanStack Query gives consistent loading/error states, avoids duplicate requests, and simplifies polling for report generation and knowledge ingest status.

**Alternatives considered**:

- **Astro + React islands**: Astro is best when there is significant static or server-rendered content; here almost every flow is interactive, so we would end up with many `client:load` islands or a single large React app inside Astro with little benefit over a pure Vite+React SPA.
- **Refine**: Strong fit for admin panels and REST-backed UIs (resources, useTable, useForm). Rejected for MVP to keep stack minimal and avoid learning curve; we can adopt later if the app grows.
- **React Admin**: Batteries-included data-driven UI (Material Design). Rejected for same reason as Refine; Material and resource model not required for the current scope.
- **Log-specific UIs (Telescope, OpenObserve)**: Used as UX inspiration only (log table, filters, time range); not used as a framework.

---

## 2. API integration and data fetching

**Decision**: **TanStack Query** for all server state; **fetch** (or a thin wrapper) for the actual HTTP calls to the backend base URL (configurable via env, e.g. `VITE_API_BASE`). No GraphQL or code generation for MVP.

**Rationale**: Backend already exposes REST endpoints for sessions, upload, logs/query, knowledge ingest/search, reports (list/get/generate/export). CORS is enabled. TanStack Query provides: caching and deduplication of GET requests (e.g. session list, report list, report detail); polling for report generation and knowledge ingest status; consistent loading/error/empty states; and invalidation after mutations (e.g. create session → refetch session list). The API client remains a simple module that builds URLs and handles JSON and file upload/export; Query uses it inside `queryFn` / `mutationFn`.

**Alternatives considered**: GraphQL or OpenAPI codegen would add tooling and complexity without a current need. SWR is a lighter alternative to TanStack Query; TanStack Query was chosen for its polling and mutation APIs that fit report generation and ingest flows well.

---

## 3. Metrics and dashboards (Grafana link)

**Decision**: **Link only** — frontend provides a link that opens Grafana (or configured dashboard URL) in a new tab/window with session context (e.g. query param or dashboard variable for `session_id`). No embedding of Grafana in the app.

**Rationale**: Aligned with spec clarification: "Link only; open session-scoped metrics/dashboards in a new tab/window." Grafana URL is configurable (e.g. `VITE_GRAFANA_URL` defaulting to `http://localhost:3000`); frontend builds the link with current session so the opened view is session-scoped.

**Alternatives considered**: Embedding Grafana (iframe) was explicitly out of scope per spec.

---

## 4. State and routing

**Decision**: **TanStack Query for server state** (sessions, reports, logs, knowledge); **React state or a small context** for client-only state (e.g. current session id, selected report id); **React Router** for top-level routes (e.g. session list, session detail/upload/search/reports).

**Rationale**: Server state is owned by TanStack Query (cache, refetch, invalidation). Global client state is minimal (current session id, UI toggles). React Router keeps URLs shareable and supports back/forward.

**Alternatives considered**: Redux/Zustand can be added later if client state grows; not required for Phase 1.

---

## 5. Accessibility (MVP)

**Decision**: **Keyboard navigation, logical focus order, and meaningful labels** for main flows (session list/selection, upload, log search, report trigger/view, export). No formal WCAG audit or conformance claim for MVP.

**Rationale**: Spec states: "Basic accessibility in scope for MVP: keyboard navigation and focus order for main flows; meaningful labels for screen readers where practical."

**Alternatives considered**: Full WCAG 2.1 AA audit and remediation deferred post-MVP.

---

## 6. TanStack Query (data fetching)

**Decision**: **@tanstack/react-query** as the primary way to fetch and mutate server data. Use `useQuery` for GETs (session list, report list, report by id, logs query, knowledge search, ingest status); use `useMutation` for POST/PATCH (create/update session, upload, generate report, trigger ingest). Use query invalidation after mutations so lists and details stay in sync. Use polling (e.g. `refetchInterval`) for report generation and ingest status until completion.

**Rationale**: Reduces boilerplate for loading/error states, avoids duplicate in-flight requests, standardizes caching and refetch behavior, and makes polling and cache invalidation straightforward. Fits the mix of one-off fetches (log search), list + detail (sessions, reports), and long-running async (report generation, ingest) very well.

**Alternatives considered**: SWR (simpler but less flexible for mutations and polling); raw fetch + useState/useEffect (more code and easy to get wrong for caching and dedup).

---

## 7. Zod, React Hook Form, date-fns

**Decision**: **Zod** for validation (API response schemas and form schemas); **React Hook Form** for form state (create session, report question, knowledge search, log filters); **date-fns** for formatting timestamps and ISO dates in the UI.

**Rationale**: Zod gives a single source of truth for shapes and runtime validation with good TypeScript inference; use with TanStack Query’s `select` or in a small parse layer and with React Hook Form’s `zodResolver`. React Hook Form keeps re-renders low and integrates cleanly with mutations. date-fns is modular (e.g. `format`, `parseISO`) and avoids ad-hoc string handling for `timestamp_ns` and `created_at`.

**Alternatives considered**: Yup (similar to Zod; Zod preferred for TS inference). dayjs (lighter than date-fns; date-fns chosen for consistency and tree-shaking). Formik (heavier than React Hook Form; RHF chosen for performance and resolver ecosystem).

---

## 8. Sonner and DaisyUI toasts

**Decision**: Use **Sonner** for toast behavior (imperative API, stacking, auto-dismiss) and style toasts with **DaisyUI’s alert component** so they match the app theme.

**Can Sonner use the toast that DaisyUI provides?** DaisyUI’s “toast” is only a **container** (`.toast`) that stacks **alert** elements (`.alert`, `.alert-success`, `.alert-error`, `.alert-info`). It does not provide show/hide, timing, or stacking logic—you’d implement that yourself. Sonner, by contrast, provides the full behavior (`toast.success()`, `toast.error()`, stacking, dismiss). So we use **Sonner for behavior** and **DaisyUI’s alert styling for the look**: configure Sonner with `unstyled` and `toastOptions.classNames.toast` so each toast’s wrapper gets DaisyUI classes (e.g. `alert alert-success` for success, `alert alert-error` for error). Optionally use Sonner’s `icons` prop with DaisyUI-style icons or pass custom JSX per toast. Result: toasts that look like DaisyUI alerts (same colors and theme) with Sonner’s API and lifecycle.

**Rationale**: Single toast API (`toast.success()`, etc.) from Sonner; consistent visual style with the rest of the app (DaisyUI alert); no need to build a custom toast manager around DaisyUI’s container.

---

## 9. Optional additions

| Library | Purpose | Benefit |
|--------|---------|---------|
| **ky** | HTTP client | Tiny fetch wrapper with base URL and error handling; TanStack Query works with raw fetch too. |

Add only if the team wants a dedicated HTTP client layer.

---

## References

- [Vite](https://vitejs.dev/)
- [React](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [DaisyUI](https://daisyui.com/)
- [TanStack Query](https://tanstack.com/query/latest) — data fetching and server state.
- [Zod](https://zod.dev/) — schema validation.
- [React Hook Form](https://react-hook-form.com/) — form state; [Zod resolver](https://github.com/react-hook-form/resolvers#zod).
- [date-fns](https://date-fns.org/) — date formatting.
- [Sonner](https://sonner.emilkowal.ski/) — toasts; [styling with classNames](https://sonner.emilkowal.ski/styling) for DaisyUI alert look.
- [research-frontend-tech.md](./research-frontend-tech.md) — earlier comparison of Astro, Refine, React Admin.
