# UI Contract: Sidebar Session List Scroll Region

**Branch**: 008-scrollable-session-list-titles  
**Date**: 2026-03-15  

Describes the layout behavior so the session list scrolls independently inside the sidebar; the rest of the page (main content) does not scroll when the user scrolls the list.

---

## 1. Sidebar structure

**Regions (top to bottom)**:
1. **Fixed header**: "Sessions" heading + "Current: …" (or "No session selected"). Not scrollable.
2. **Create session form**: Fixed; not inside the scroll region.
3. **Scroll region**: Contains only the session list (and its pagination controls, e.g. "Load more", "Previous"). This region scrolls independently with `overflow-y: auto` (or equivalent).

**Layout**:
- Sidebar is a flex column (`flex flex-col`).
- Header and form have natural height; scroll region takes remaining space with `flex-1 min-h-0` and `overflow-y: auto` so it can shrink and scroll.
- Main content area is a sibling of the sidebar; it may have its own overflow. Scrolling inside the sidebar scroll region MUST NOT cause the main content or the overall page to scroll.

---

## 2. Scroll behavior

- **User scrolls inside the list region**: Only the session list content scrolls; the "Sessions" header, "Current" line, Create form, and main content stay fixed.
- **Many sessions**: List grows vertically inside the scroll region; scrollbar appears on the scroll region only.
- **Few sessions**: No unnecessary scrollbar; region height is flexible (min-h-0 allows it to shrink).

---

## 3. Implementation note

In CSS Flexbox, a flex child defaults to `min-height: auto`, which can prevent it from shrinking below content height. Setting `min-h-0` (Tailwind) or `min-height: 0` on the scroll container allows it to shrink and show a scrollbar. The scroll container should wrap only the list + pagination (e.g. `<div className="flex-1 min-h-0 overflow-y-auto">...</div>` around SessionList content).
