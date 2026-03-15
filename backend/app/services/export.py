"""Report export: Markdown (return content) and PDF (ReportLab, pure Python)."""

from __future__ import annotations

import html
import logging
import re
from html.parser import HTMLParser
from io import BytesIO
from typing import Literal

import markdown
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)


def export_markdown(content: str) -> str:
    """Return report content as Markdown with consistent formatting for viewers."""
    if not content or not content.strip():
        return ""
    # Normalize: collapse 3+ newlines to 2, ensure single trailing newline
    normalized = re.sub(r"\n{3,}", "\n\n", content.strip())
    return normalized + "\n"


def _strip_tags(html_fragment: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", html_fragment)
    text = re.sub(r"\s+", " ", text).strip()
    return html.unescape(text)


BlockItem = tuple[
    str, str, Literal["ol", "ul"] | None, int | None, str | None
]  # tag, text, list_type, ol_index, raw_html (for p only)


class _ReportHTMLParser(HTMLParser):
    """Parse HTML from Markdown into (tag, text, list_type, ol_index, raw_html) for block elements."""

    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[BlockItem] = []
        self._list_stack: list[Literal["ol", "ul"]] = []
        self._ol_index = 0
        self._current_tag: str | None = None
        self._current_text: list[str] = []
        self._current_raw: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_l = tag.lower()
        if self._current_tag == "p":
            self._current_raw.append(f"<{tag_l}>")
        if tag_l == "ol":
            self._list_stack.append("ol")
            self._ol_index = 0
        elif tag_l == "ul":
            self._list_stack.append("ul")
        elif tag_l in ("h1", "h2", "h3", "h4", "p", "pre", "li"):
            self._current_tag = tag_l
            self._current_text = []
            self._current_raw = []
            if tag_l == "li" and self._list_stack and self._list_stack[-1] == "ol":
                self._ol_index += 1

    def handle_endtag(self, tag: str) -> None:
        tag_l = tag.lower()
        if tag_l in ("ol", "ul"):
            if self._list_stack:
                self._list_stack.pop()
        elif tag_l == self._current_tag and self._current_tag is not None:
            text = _strip_tags("".join(self._current_text)).strip()
            raw_html = "".join(self._current_raw).strip() if self._current_tag == "p" else None
            if text:
                list_type: Literal["ol", "ul"] | None = (
                    self._list_stack[-1] if self._list_stack else None
                )
                index: int | None = self._ol_index if list_type == "ol" else None
                self.blocks.append((self._current_tag, text, list_type, index, raw_html))
            self._current_tag = None
            self._current_text = []
            self._current_raw = []
        elif self._current_tag == "p":
            self._current_raw.append(f"</{tag_l}>")

    def handle_data(self, data: str) -> None:
        if self._current_tag is not None:
            self._current_text.append(data)
            if self._current_tag == "p":
                self._current_raw.append(data)


def _html_blocks_to_flowables_data(html_str: str) -> list[BlockItem]:
    """Extract block-level elements with list context: (tag, text, list_type, ol_index)."""
    parser = _ReportHTMLParser()
    parser.feed(html_str)
    blocks = parser.blocks
    if not blocks:
        text = _strip_tags(html_str).strip()
        if text:
            blocks = [("p", text, None, None, None)]
    return blocks


# Characters where we prefer to break long code lines (ReportLab-compatible set).
_PRE_WRAP_SPLIT_CHARS = frozenset(" :.,;/-\\()[]{}")


def _wrap_pre_lines(text: str, max_len: int = 78) -> str:
    """Wrap long lines in preformatted text to avoid PDF overflow and ReportLab CPU hang.

    ReportLab's Preformatted with maxLineLength can be very slow or hang on large
    reports with long lines. We do a single-pass wrap here and pass the result
    without maxLineLength.
    """
    if not text or max_len < 1:
        return text
    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        if len(line) <= max_len:
            out.append(line)
            continue
        pos = 0
        while pos < len(line):
            chunk = line[pos : pos + max_len]
            if len(chunk) < max_len:
                out.append(chunk)
                break
            # Prefer break at last occurrence of a split char in this chunk
            break_at = -1
            for i in range(len(chunk) - 1, -1, -1):
                if chunk[i] in _PRE_WRAP_SPLIT_CHARS:
                    break_at = i
                    break
            if break_at >= 0:
                out.append(chunk[: break_at + 1].rstrip())
                pos += break_at + 1
                # Skip leading spaces on continuation
                while pos < len(line) and line[pos] == " ":
                    pos += 1
            else:
                out.append(chunk)
                pos += max_len
    return "\n".join(out)


def _paragraph_to_reportlab_markup(raw_html: str | None, plain_text: str) -> str:
    """Convert paragraph HTML to ReportLab Paragraph markup; preserve <code> as Courier font."""
    if not raw_html or "<code>" not in raw_html:
        return html.escape(plain_text)
    result: list[str] = []
    i = 0
    raw_lower = raw_html.lower()
    while i < len(raw_html):
        if raw_lower[i : i + 6] == "<code>":
            result.append('<font face="Courier" size="9">')
            i += 6
            end = raw_lower.find("</code>", i)
            if end == -1:
                result.append(html.escape(raw_html[i:]))
                break
            result.append(html.escape(raw_html[i:end]))
            result.append("</font>")
            i = end + 7
        else:
            next_lt = raw_html.find("<", i)
            if next_lt == -1:
                result.append(html.escape(raw_html[i:]))
                break
            result.append(html.escape(raw_html[i:next_lt]))
            i = next_lt
    return "".join(result)


def _pdf_footer_first(canvas, doc) -> None:
    """Draw title and footer on first page."""
    canvas.saveState()
    page_w = 8.5 * inch
    page_h = 11 * inch
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(page_w / 2, page_h - 0.75 * inch, "Incident Report")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(page_w / 2, 0.5 * inch, "Page 1  ·  Generated by LogPilot")
    canvas.restoreState()


def _pdf_footer_later(canvas, doc) -> None:
    """Draw page number on later pages."""
    canvas.saveState()
    page_w = 8.5 * inch
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(page_w / 2, 0.5 * inch, f"Page {page_num}  ·  Generated by LogPilot")
    canvas.restoreState()


def export_pdf(content: str) -> bytes:
    """Render report Markdown to PDF using ReportLab (pure Python, no system deps)."""
    html_str = markdown.markdown(content, extensions=["extra"])
    blocks = _html_blocks_to_flowables_data(html_str)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=(8.5 * inch, 11 * inch),
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=0.75 * inch,  # room for footer
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        spaceAfter=12,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "ReportH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    def _h2_divider() -> Table:
        t = Table([[""]], colWidths=[6.5 * inch], rowHeights=[3])
        t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.grey)]))
        t.keepWithNext = True  # keep section divider with first content of section
        return t
    h3_style = ParagraphStyle(
        "ReportH3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        spaceAfter=6,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        spaceAfter=6,
    )
    code_style = ParagraphStyle(
        "ReportCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=10,
        backColor="#e8e8e8",
        leftIndent=12,
        rightIndent=12,
        spaceBefore=6,
        spaceAfter=8,
    )

    story: list = [Spacer(1, 0.2 * inch)]  # space below "Incident Report" on first page
    for item in blocks:
        tag, text, list_type, ol_index, raw_html = item
        escaped = html.escape(text)
        if tag == "h1":
            story.append(Paragraph(escaped, title_style))
        elif tag == "h2":
            story.append(Paragraph(escaped, h2_style))
            story.append(_h2_divider())
        elif tag in ("h3", "h4"):
            story.append(Paragraph(escaped, h3_style))
        elif tag == "pre":
            # Preformatted draws the string as-is; do not pass html.escape(text) or
            # entities like &quot; and &#x27; appear literally. Unescape so quotes
            # and apostrophes render correctly.
            pre_text = html.unescape(text)
            # Pre-wrap long lines to avoid PDF overflow and to avoid ReportLab's
            # internal line-breaking (which can hang or exhaust memory on large reports).
            pre_text = _wrap_pre_lines(pre_text, max_len=78)
            story.append(Preformatted(pre_text, code_style))
        elif tag == "li":
            if list_type == "ol" and ol_index is not None:
                story.append(Paragraph(f"{ol_index}. {escaped}", body_style))
            else:
                story.append(Paragraph(f"• {escaped}", body_style))
        elif tag == "p":
            p_markup = _paragraph_to_reportlab_markup(raw_html, text)
            story.append(Paragraph(p_markup, body_style))
        else:
            story.append(Paragraph(escaped, body_style))
        # Tighter spacing after list items so lists stay grouped across pages
        spacer_pt = 2 if tag == "li" else 6
        story.append(Spacer(1, spacer_pt))

    if len(story) <= 1:  # only initial spacer or empty
        fallback = html.escape(content.replace("\n", "<br/>"))
        story.append(Paragraph(fallback, body_style))

    doc.build(story, onFirstPage=_pdf_footer_first, onLaterPages=_pdf_footer_later)
    buf.seek(0)
    return buf.read()
