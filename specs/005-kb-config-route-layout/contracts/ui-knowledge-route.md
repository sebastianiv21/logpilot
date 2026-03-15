# UI Contract: Knowledge base route and navbar control

**Branch**: `005-kb-config-route-layout`  
**Date**: 2026-03-15  

Defines the UI contract for the new knowledge base route and the upper-right control in the main-content navbar. Implementation must satisfy these so that acceptance tests and manual validation can rely on them.

---

## 1. Routes

| Path | Purpose | Content |
|------|---------|---------|
| `/` | Home (main screen) | Session intro, Upload logs, Logs & metrics, Reports. No knowledge base section. |
| `/knowledge` | Knowledge base page | Knowledge base ingestion and search only; visible in-app return to home. |

Direct navigation to `/knowledge` (e.g. bookmark, URL bar) must render the knowledge page without requiring a session. Browser back from `/knowledge` returns to previous page.

---

## 2. Upper-right control (all pages using AppLayout)

- **Placement**: In the main-content navbar (horizontal bar above the page content), top-right. Visible on home and on the knowledge page. The navbar is distinct from the left sidebar (sessions).
- **Visual**: Database icon only + status indicator (small colored dot). No visible text label.
- **Tooltip**: On hover or focus, tooltip text MUST be "Knowledge base".
- **Interaction**: Single click (or activation) navigates to `/knowledge` (or the configured knowledge route). No dropdown or menu.
- **Status indicator**:
  - **Red**: No knowledge base, empty, or last ingestion run failed.
  - **Yellow/ochre**: Ingestion in progress; MUST have a pulsating effect.
  - **Green**: Knowledge base available and complete.
- **Accessibility**: Focusable via keyboard; announced as "Knowledge base" (e.g. `aria-label` or `title`); status (no data / ingesting / ready) communicated to assistive technologies.

---

## 3. Knowledge page

- **Content**: Single section containing (1) knowledge base ingestion controls and (2) knowledge search. Grouped and labeled as one coherent "Knowledge base" area.
- **Return**: Visible in-app control (e.g. "Back to home" or "Home" link/button) that navigates to `/`. Browser back also returns to previous screen.
- **No session required**: Page is usable without a session selected (KB is global).

---

## 4. Main screen (home)

- **Sections**: Session intro, Upload logs, Logs & metrics, Reports — in that order. No knowledge base block.
- **Layout**: Clear visual hierarchy (headings, spacing, grouping); order MUST NOT change.
