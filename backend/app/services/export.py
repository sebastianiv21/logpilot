"""Report export: Markdown (return content) and PDF (ReportLab, pure Python)."""

from __future__ import annotations

import html
import logging
import re
from html.parser import HTMLParser
from io import BytesIO
from typing import Literal

import markdown
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer

logger = logging.getLogger(__name__)


def export_markdown(content: str) -> str:
    """Return report content as Markdown (passthrough)."""
    return content


def _strip_tags(html_fragment: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", html_fragment)
    text = re.sub(r"\s+", " ", text).strip()
    return html.unescape(text)


BlockItem = tuple[str, str, Literal["ol", "ul"] | None, int | None]


class _ReportHTMLParser(HTMLParser):
    """Parse HTML from Markdown into (tag, text, list_type, ol_index) for block elements."""

    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[BlockItem] = []
        self._list_stack: list[Literal["ol", "ul"]] = []
        self._ol_index = 0
        self._current_tag: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_l = tag.lower()
        if tag_l == "ol":
            self._list_stack.append("ol")
            self._ol_index = 0
        elif tag_l == "ul":
            self._list_stack.append("ul")
        elif tag_l in ("h1", "h2", "h3", "h4", "p", "pre", "li"):
            self._current_tag = tag_l
            self._current_text = []
            if tag_l == "li" and self._list_stack and self._list_stack[-1] == "ol":
                self._ol_index += 1

    def handle_endtag(self, tag: str) -> None:
        tag_l = tag.lower()
        if tag_l in ("ol", "ul"):
            if self._list_stack:
                self._list_stack.pop()
        elif tag_l == self._current_tag and self._current_tag is not None:
            text = _strip_tags("".join(self._current_text)).strip()
            if text:
                list_type: Literal["ol", "ul"] | None = (
                    self._list_stack[-1] if self._list_stack else None
                )
                index: int | None = self._ol_index if list_type == "ol" else None
                self.blocks.append((self._current_tag, text, list_type, index))
            self._current_tag = None
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_tag is not None:
            self._current_text.append(data)


def _html_blocks_to_flowables_data(html_str: str) -> list[BlockItem]:
    """Extract block-level elements with list context: (tag, text, list_type, ol_index)."""
    parser = _ReportHTMLParser()
    parser.feed(html_str)
    blocks = parser.blocks
    if not blocks:
        text = _strip_tags(html_str).strip()
        if text:
            blocks = [("p", text, None, None)]
    return blocks


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
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "ReportH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        spaceAfter=8,
    )
    h3_style = ParagraphStyle(
        "ReportH3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        spaceAfter=6,
    )
    code_style = ParagraphStyle(
        "ReportCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=9,
        backColor="#f0f0f0",
        spaceAfter=6,
    )

    story: list = []
    for item in blocks:
        tag, text, list_type, ol_index = item
        escaped = html.escape(text)
        if tag == "h1":
            story.append(Paragraph(escaped, title_style))
        elif tag == "h2":
            story.append(Paragraph(escaped, h2_style))
        elif tag in ("h3", "h4"):
            story.append(Paragraph(escaped, h3_style))
        elif tag == "pre":
            story.append(Preformatted(escaped, code_style))
        elif tag == "li":
            if list_type == "ol" and ol_index is not None:
                story.append(Paragraph(f"{ol_index}. {escaped}", body_style))
            else:
                story.append(Paragraph(f"• {escaped}", body_style))
        else:
            story.append(Paragraph(escaped, body_style))
        # Tighter spacing after list items so lists stay grouped across pages
        spacer_pt = 2 if tag == "li" else 6
        story.append(Spacer(1, spacer_pt))

    if not story:
        fallback = html.escape(content.replace("\n", "<br/>"))
        story.append(Paragraph(fallback, body_style))

    doc.build(story)
    buf.seek(0)
    return buf.read()
