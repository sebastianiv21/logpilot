# Research: Scrollable Session List and Dynamic Session Titles with Copy ID

**Branch**: 008-scrollable-session-list-titles  
**Date**: 2026-03-15

Decisions and rationale for implementation. No NEEDS CLARIFICATION remained; all choices are guided by the spec and existing codebase.

---

## 1. Self-contained scrollable session list (sidebar)

**Decision**: Use a flex column layout for the sidebar with a dedicated scrollable region for the session list. Give the list container `flex-1 min-h-0 overflow-y-auto` (or equivalent) so it takes remaining height and scrolls independently; keep the "Sessions" heading and "Current: …" and Create form outside the scroll area.

**Rationale**: In CSS Flexbox, a flex child does not shrink below its content size unless `min-height: 0` (min-h-0 in Tailwind) is set. Without it, the sidebar can grow with content and force the whole page to scroll. Constraining the list to a scroll region with `overflow-y: auto` keeps only that region scrollable. Existing AppLayout already has `flex-1 overflow-auto` on the nav; adding an inner wrapper around SessionList + pagination with `min-h-0 flex-1 overflow-y-auto` ensures the list scrolls inside the aside while the rest of the layout stays fixed.

**Alternatives considered**:
- Rely only on existing nav overflow: Current structure may not constrain height if the flex child doesn’t shrink; explicit wrapper with min-h-0 is more reliable.
- Fixed height in pixels: Avoided; flexible height works better across viewports and with variable header/form size.

---

## 2. Copy-to-clipboard and feedback (success / failure)

**Decision**: Use the Clipboard API (`navigator.clipboard.writeText(sessionId)`). On success, show a success toast (e.g. Sonner); on failure (e.g. permission denied, not available), show an error toast with a message like "Copy failed" or "Couldn't copy". Use the same toast system (Sonner) for both.

**Rationale**: Spec requires success and failure feedback via the same channel (tooltip or toast). The app already uses Sonner for toasts; reusing it keeps UX consistent and avoids adding another feedback mechanism. Clipboard API is widely supported in modern browsers; fallback or manual copy is out of scope unless product decides otherwise.

**Alternatives considered**:
- Tooltip-only feedback: Possible but toasts are more visible and already in use; spec allows "tooltip or toast".
- document.execCommand('copy'): Deprecated; Clipboard API is the standard approach.

---

## 3. Long session name: truncate + full name on hover

**Decision**: Truncate the section title with CSS (e.g. `truncate` in Tailwind for ellipsis). Expose the full session name on hover via the native `title` attribute, or a small tooltip component if the product already has one.

**Rationale**: Spec requires truncation with ellipsis and full name on hover (e.g. tooltip). The simplest approach is `title={sessionName}` on the title element; no new dependency. If the design system already uses a custom tooltip (e.g. DaisyUI tooltip), use that for consistency.

**Alternatives considered**:
- Multi-line wrap: Spec chose truncate + hover to keep headers to one line and layout predictable.
- No tooltip: Spec explicitly requires showing full name on hover.

---

## 4. Accessible copy control

**Decision**: Use a button element (not a div with onClick) for the copy action. Give it an accessible name with `aria-label="Copy session ID"` (or `title` plus visible text if preferred). Ensure the button is focusable and keyboard-activatable. Optionally use a Lucide copy icon with `aria-hidden="true"` so screen readers rely on the label.

**Rationale**: Spec requires an accessible name (e.g. "Copy session ID") for screen readers. A semantic button with aria-label meets this and keeps keyboard and assistive tech support without extra complexity.

**Alternatives considered**:
- Icon-only with no label: Fails accessibility requirement.
- Visible "Copy" text: Acceptable; spec allows "e.g. Copy session ID"; aria-label is sufficient if the control is icon-only.

---

## 5. Session ID prefix length (first part of ID)

**Decision**: Use the same length already used in the session list/sidebar. In the current codebase, `SessionList.tsx` uses `session.id.slice(0, 8)` for display when the session has no name (e.g. "Session f4bee7b1"). Use 8 characters for section titles when the session has no name so behavior is consistent.

**Rationale**: Spec and clarifications say to match existing UI; no new constant or configuration needed.

**Alternatives considered**: None; spec explicitly defers to existing convention.
