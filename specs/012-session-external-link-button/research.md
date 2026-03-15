# Research: Session External Link Button in Main Content

**Branch**: `012-session-external-link-button`  
**Date**: 2026-03-15  

## 1. Opening external link in new tab (security and behavior)

**Decision**: Use an `<a href={external_link}>` with `target="_blank"` and `rel="noopener noreferrer"`.

**Rationale**: Spec requires opening in a new tab so the app stays open. `rel="noopener"` prevents the new page from accessing `window.opener`; `rel="noreferrer"` avoids sending the Referer header to the target site. This is the standard, secure pattern for external links.

**Alternatives considered**:
- `window.open(url, '_blank')`: works but requires JavaScript and does not give the same semantics as a link (e.g. "open in new tab" via context menu). Using a real anchor is better for accessibility and behavior.
- Same-tab navigation: spec clarification chose new tab; rejected.

## 2. Icon + visible text and accessibility

**Decision**: Use lucide-react’s `ExternalLink` (or equivalent) icon plus visible text "External link". Give the control an accessible name: either use the visible text as the link text (so "External link" is the default accessible name) or add `aria-label="Open session's external link"` for fuller context in screen readers.

**Rationale**: Spec FR-005 requires both an icon and the visible text "External link", and that the control be keyboard-focusable with an accessible name. An `<a>` with text and an icon (with `aria-hidden="true"` on the icon so only the text is announced, or a single aria-label on the link) satisfies this. Placement next to the session title already associates it with the session’s external link.

**Alternatives considered**:
- Icon-only with tooltip: spec clarification chose icon + visible text "External link"; rejected.
- Button that calls `window.open`: anchor is preferable for semantics (it’s a link) and right-click "open in new tab"; use anchor unless product requires a button for styling consistency (then ensure it has role and href semantics or equivalent).

## 3. When to enable vs disable the control (empty / whitespace)

**Decision**: The control is always shown next to the session title. Treat `external_link` as "present" only when it is a non-empty string after trimming whitespace. When present, the control is enabled (clickable link). When `external_link` is `null`, `undefined`, or `''` or only whitespace, the control is disabled and MUST show a tooltip (e.g. "No external link provided" or "There is no provided link") so users understand why it cannot be activated.

**Rationale**: Spec update: when no link is provided, show the icon disabled with a tooltip instead of hiding the control. This makes the feature discoverable and explains the missing link. Frontend should normalize with `external_link?.trim()` and set enabled/disabled + tooltip accordingly.

**Alternatives considered**:
- Hide control when no link: previous behavior; user requested disabled + tooltip instead.
- Validate URL format before enabling: spec says URL validation is out of scope; we only check presence/non-emptiness.
