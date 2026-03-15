# UI Contract: Session Search Bar

**Branch**: 009-session-search-bar  
**Date**: 2026-03-15  

Describes the session search input and its relationship to the session list: placement, behavior, and accessibility.

---

## 1. Placement and layout

- **Location**: Directly above the scrollable session list in the sidebar, same column. Order (top to bottom): Sessions heading → Create session form → **Session search input** → Scroll region containing the session list.
- **Visibility**: Shown on the same views where the session list is shown (e.g. not on the knowledge page when the sidebar is hidden). When the sidebar is visible, the search bar is always visible above the list (not inside the scroll region).
- **Layout**: Search input does not scroll with the list; it remains fixed above the scroll region. The scroll region retains `flex-1 min-h-0 overflow-y-auto` (or equivalent) so only the list scrolls.

---

## 2. Input behavior

- **Control**: Single text input (search bar). No separate "Search" or "Submit" button; filtering is driven by the input value.
- **Trim**: Leading and trailing whitespace are trimmed before applying the filter. Whitespace-only input is treated as empty → show full session list.
- **Debounce**: The filtered list updates after a short pause (150–300 ms, e.g. 200 ms) after the user stops typing. The input value itself may update on every keystroke; the filter is applied using a debounced value.
- **Clear**: When the user clears the input (or leaves it empty/whitespace-only), the full session list is shown. A clear control (e.g. button to clear the field) is optional but recommended for one-step restore (SC-003).

---

## 3. Matching rules

- **Fields**: Session is included if the (trimmed, debounced) query appears as a substring in any of: session name, session ID, external link. Null name or external_link is treated as empty string for matching.
- **Case**: Case-insensitive (e.g. "incident" matches "Incident #123").
- **Literal**: Plain substring match; no regex or special interpretation of characters. Characters that might look like regex are matched literally.

---

## 4. List and empty state

- **Filtered list**: Only sessions matching the (trimmed, debounced) query are shown in the scrollable list. Pagination (e.g. "Load more") applies to the filtered list.
- **Empty state when no matches**: When at least one session exists in the full list but none match the current search, show a single clear message (e.g. "No sessions match your search") inside the list area so the user knows the result is from the filter.
- **Empty state when no sessions**: When there are no sessions at all, keep the existing message (e.g. "No sessions yet. Create one to get started."). The two states (no sessions vs. no matches) must be distinguishable.

---

## 5. Accessibility

- **Input label**: The search input MUST have an accessible name, e.g. via `aria-label="Search sessions by name, ID, or link"` or a visible `<label>` associated with the input, so assistive technologies can identify it.
- **Live region**: The system MUST expose the filter result to assistive technologies. Use a live region (e.g. `aria-live="polite"`, `aria-atomic="true"`) that announces:
  - When there are matching sessions: the number of matches (e.g. "3 sessions" or "1 session").
  - When the filter is applied and there are no matches: "No sessions match your search" (or equivalent).
- **Timing**: Update the live region when the debounced filter result changes so the announcement matches what the user sees after the pause.

---

## 6. Implementation note

The search input can be implemented in AppLayout (sidebar) and the filter applied either in the same component (passing filtered sessions to SessionList) or inside SessionList via a `searchQuery` prop. The debounced value and filter logic must be shared so the list and live region stay in sync with the same debounced query.
