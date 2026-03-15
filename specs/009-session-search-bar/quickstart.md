# Quickstart: Session Search Bar

**Branch**: 009-session-search-bar  
**Date**: 2026-03-15  

Minimal steps to run and validate the session search bar. Assumes the full stack (backend and frontend) is running per project docs.

---

## Prerequisites

- **Backend** at `http://localhost:8000` (or `VITE_API_BASE`).
- **Frontend** dev server running (e.g. `cd frontend && pnpm dev`).
- **At least a few sessions** with varied names, IDs, and optionally external links so search can be tested.

---

## 1. Locate the search bar

1. Open the app at `/` and ensure the **Sessions** sidebar is visible (not on the knowledge page).
2. Confirm a **search input** appears **directly above** the session list in the sidebar (below the Create session form, above the scrollable list).
3. Confirm the search bar stays visible when scrolling the session list (it does not scroll with the list).

---

## 2. Filter by name, ID, or external link

1. **By name**: Type part of a session name (e.g. "incident"). After a short pause (~200 ms), the list should show only sessions whose name contains that text (case-insensitive). Clear the input; full list returns.
2. **By session ID**: Type part of a session ID (e.g. first few characters). List filters to sessions whose ID contains that substring. Clear; full list returns.
3. **By external link**: If any session has an external link, type part of the URL. List filters to sessions whose external link contains that text. Clear; full list returns.
4. Confirm matching is **case-insensitive** (e.g. "INCIDENT" matches "Incident #123").

---

## 3. Whitespace and empty input

1. Enter spaces only (e.g. "   "). Confirm the **full session list** is shown (trimmed value is empty).
2. Enter text then clear the input (or delete all characters). Confirm the full list is restored.

---

## 4. Empty state when no matches

1. With at least one session in the list, type text that **matches no session** (e.g. "xyznonexistent").
2. After the debounce, confirm a clear message such as **"No sessions match your search"** (or equivalent) appears in the list area, not a blank list with no explanation.
3. Clear the search; confirm the full list returns and the empty-state message is no longer shown.
4. Confirm that when there are **no sessions at all**, the message is different (e.g. "No sessions yet") so the two states are distinguishable.

---

## 5. Debounce

1. Type several characters quickly. Confirm the list updates **after** you stop typing (short delay ~150–300 ms), not on every single keystroke.
2. If a clear control exists, use it and confirm the list restores in one action.

---

## 6. Accessibility

1. **Label**: Focus the search input (keyboard tab). Confirm it has an accessible name (e.g. "Search sessions by name, ID, or link") via screen reader or dev tools.
2. **Live region**: After filtering, confirm assistive tech announces the result (e.g. "3 sessions" or "No sessions match your search") when the debounced result updates. If using a screen reader, trigger a filter and listen for the announcement after the pause.

---

## 7. Re-check after implementation

- Search bar is above the scrollable list; list filters by name, ID, external link; case-insensitive; trim and debounce behave as above; empty state and a11y (label + live region) are present.
