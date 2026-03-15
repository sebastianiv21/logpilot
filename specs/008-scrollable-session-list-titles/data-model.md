# Data Model: Scrollable Session List and Dynamic Session Titles with Copy ID

**Branch**: 008-scrollable-session-list-titles  
**Date**: 2026-03-15  
**Source**: Feature spec; UI/display state only. No new backend entities or persistence.

---

## 1. Current session for display (derived)

**Source**: Existing `Session` (id, name, external_link, created_at, updated_at) and `currentSessionId` from SessionContext. Look up current session from sessions list by `currentSessionId`; if not found, treat as no session.

- **Display title**: If current session has a name, use it; else `"Session " + id.slice(0, 8)` (match session list convention).
- **Full session ID**: `session.id` (full string) for display and copy.
- **No session**: When `currentSessionId` is null or not in list, show placeholder title "No session selected"; hide session ID line and copy control.

No new API or storage. Derived in the component that renders section headers (e.g. from `useSessionsList().data?.sessions` and `useCurrentSession().currentSessionId`).

---

## 2. Sidebar scroll region (layout)

- **Region**: A wrapper element that contains only the session list (and pagination controls). It has a constrained height (flex child with `flex-1 min-h-0`) and `overflow-y: auto` so only this region scrolls.
- **Outside scroll**: "Sessions" heading, "Current: …" line, and Create session form remain above the scroll region and do not scroll with the list.

No persistent state; layout only.

---

## 3. Section header (Logs & metrics / Reports)

- **Title**: String — either current session name, or "Session " + first 8 chars of ID, or placeholder "No session selected" when no session.
- **Long name**: Truncated with ellipsis in UI; full name in `title` (or tooltip) for hover. No new field; display logic only.
- **Session ID line**: Shown only when there is a current session; displays full `session.id` and a copy button with accessible name "Copy session ID".
- **Copy feedback**: Success/failure shown via toast (Sonner); no persistent state.

Validation: Title and ID line update immediately when `currentSessionId` or session data changes.

---

## 4. Copy control state (ephemeral)

- **Action**: User clicks copy → `navigator.clipboard.writeText(sessionId)`.
- **Success**: Toast success (e.g. "Session ID copied").
- **Failure**: Toast error (e.g. "Copy failed" or "Couldn't copy").
- No retry or persistence; one-shot feedback only.

---

## 5. Session list ID prefix (constant)

- **Length**: 8 characters (already used in SessionList: `session.id.slice(0, 8)`).
- **Where used**: Section titles when session has no name; consistent with sidebar list display.

No new entities. Backend Session schema unchanged.
