# Data Model: Session External Link Button in Main Content

**Branch**: `012-session-external-link-button`  
**Date**: 2026-03-15  

This feature does not introduce new entities or persisted data. It consumes the existing Session’s optional `external_link` field and always shows a UI control that is enabled when that value is present and non-empty, and disabled with a tooltip when it is not.

## Existing entities (unchanged)

- **Session**: Already includes optional `external_link` (string | null) from the sessions API. Provided at session creation or via PATCH; stored in backend and returned in GET session and GET sessions list. The main-content external link control is always shown; it is enabled when `external_link` is a non-empty string (after trimming whitespace) and disabled with a tooltip (e.g. "No external link provided") when `external_link` is missing, null, or empty/whitespace-only.

## In-app state

- No new frontend state. The control is derived from the current session (from existing SessionContext / useSessionsList and currentSessionId). When the user switches sessions or session data is updated (e.g. after edit), the control’s enabled/disabled state and tooltip update from the same session source.

## Validation rules (from spec)

- Control is always visible when the session title is shown. It is enabled only when the current session has a non-empty `external_link` (after trimming); otherwise it is disabled and shows a tooltip (e.g. "No external link provided").
- When enabled, the link opened MUST be the value stored for the current session (no client-side modification of the URL beyond using it as the anchor `href`).
- No URL validation or sanitization required by this feature; browser handles navigation and failures.

## State transitions

1. User selects a session → main content shows that session’s title and the "External link" control; the control is enabled if that session has non-empty `external_link`, otherwise disabled with tooltip.
2. User activates the control (when enabled) → browser opens `external_link` in a new tab (same session context; app remains in current tab). When disabled, activation does nothing.
3. User switches session or session is updated (e.g. PATCH removes or adds `external_link`) → on next render, the control’s enabled/disabled state and tooltip reflect the current session’s `external_link` value.
