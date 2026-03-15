# Research: UI polish — icons, copy, loading cues, report-ready feedback

**Branch**: `004-ui-polish-feedback`  
**Date**: 2026-03-15  

Resolves technical choices for Phase 1 design. No NEEDS CLARIFICATION remained in Technical Context; this document records decisions and alternatives.

---

## 1. Visual loading indicators

**Decision**: Use DaisyUI loading components (e.g. `loading loading-spinner`) and/or skeleton placeholders where appropriate; keep or add `aria-busy` and `role="status"` for assistive tech. Prefer inline spinners for buttons and list-level skeletons for full-page loads (e.g. report list, session list).

**Rationale**: Existing codebase already uses DaisyUI (e.g. `loading loading-spinner loading-sm` in UploadLogs). Consistency with design system and minimal new dependencies. FR-001 and FR-006 require visible, recognizable loading states.

**Alternatives considered**: Custom CSS-only spinners (more code, no benefit over DaisyUI); third-party skeleton library (extra dependency when DaisyUI + Tailwind can achieve simple skeletons).

---

## 2. Report-ready notification (toast + sound)

**Decision**: Trigger notification when report content becomes available in the existing polling loop inside `ReportGenerationContext`. On transition from “generating” to “ready”: (1) call Sonner `toast.success(...)` with context-aware message (session name or “Report ready” when single), (2) play a short, subtle sound once (throttled/queued when multiple reports complete in quick succession). Sound implemented via a small audio asset (e.g. MP3/OGG) or Web Audio API oscillator; first play after user gesture to satisfy autoplay policies.

**Rationale**: ReportGenerationContext already polls and detects when `report.content` is non-empty and then clears that session from `generatingBySession`. The same transition is the natural place to fire toast and sound. Sonner is already used for success/error toasts. Spec requires toast to work without sound for accessibility.

**Alternatives considered**: Separate service/event bus for “report ready” (unnecessary complexity); browser Notification API (toast is in-app and sufficient); sound-only without toast (rejected per spec).

---

## 3. Subtle sound implementation

**Decision**: Use a short (e.g. 200–400 ms), low-volume asset (e.g. soft chime or beep) in a format supported by the project (e.g. MP3 or OGG), played via `new Audio(src).play()`. If multiple reports become ready in quick succession, queue or throttle so only one sound plays at a time. No sound if user has not yet performed a gesture in the session (autoplay); first sound can follow the “report generation started” user action.

**Rationale**: Small asset is simple and avoids Web Audio API complexity. Throttling/queuing avoids overlapping playback (spec and Clarifications).

**Alternatives considered**: Web Audio API oscillator (no asset; more code; acceptable if asset is undesirable). System beep (not available in browser). Rely only on toast (spec requires both toast and sound; sound is best-effort for accessibility).

---

## 4. Icons (Lucid React icons)

**Decision**: Use `lucide-react` for icons. Add as dependency if not already in `frontend/package.json`. Apply icons to primary actions and section headings where they aid recognition (e.g. upload, export, generate report, search, sessions, reports). Use consistent size (e.g. `size={18}` or `className="w-4 h-4"`) and avoid putting icons on every label or every button.

**Rationale**: User requested “Lucid React icons”; spec says use where appropriate and don’t overuse. Lucide is tree-shakeable and matches React/TS stack.

**Alternatives considered**: DaisyUI icons (if any); other icon sets (user specified Lucid). No change from decision.

---

## 5. Copy review scope and process

**Decision**: Review all user-facing strings in the main app (sessions, reports, log search, knowledge, upload, connection banner, modals) and simplify for clarity and consistency. No automated i18n in scope; single pass of inline copy updates in components and toasts. Prefer short labels and non-technical error/empty messages where possible.

**Rationale**: Spec FR-004 and Clarifications define scope. Implementation is straightforward find-and-improve in existing components.

**Alternatives considered**: Extract strings to a constants file (optional, can be done later); machine translation (out of scope).

---

## 6. Integration point for “report ready”

**Decision**: In `ReportGenerationContext`, when the poll finds a report with non-empty content, before (or when) removing that session from `generatingBySession`, invoke a callback or side effect that: (1) shows the toast with context-aware message, (2) enqueues or plays the subtle sound (throttled). The context may accept an optional “onReportReady(sessionId, reportId, sessionLabel?)” callback provided by the app, or the context may import toast + sound helper directly to keep the integration in one place.

**Rationale**: Single place detects “report just became ready”; keeps polling logic and notification behavior co-located and testable.

**Alternatives considered**: Emitting from ReportView when `hasContent` flips (would miss background case when user is not on ReportView). Using a separate polling hook (duplicates polling logic). Central context remains the right place.

---

## 7. Session label for report-ready toast (context-aware message)

**Decision**: When building the report-ready toast message and multiple sessions have reports generating, resolve the session display label using the existing sessions API: call `getSession(sessionId)` from `frontend/src/services/api.ts`. The returned `Session` type has `name` and `id`; use `session.name || session.id` (or a short id slice) for the toast, e.g. "Report ready (Session X)" or "Report ready in &lt;name&gt;". The notification helper or ReportGenerationContext can perform this fetch when it needs to show a context-aware message (e.g. when `generatingBySession` has more than one entry), or accept a resolver callback to avoid coupling the context to the API.

**Rationale**: Session list is already loaded via `getSessions()` and individual session via `getSession(id)`; no new API or entity. Keeps implementation simple and consistent with existing Session type.

**Alternatives considered**: Passing session name from the component that starts generation (would not have names for reports started in other sessions). Storing a sessionId → name map in context (adds state; getSession on demand is sufficient).
