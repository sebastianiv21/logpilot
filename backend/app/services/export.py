"""Report export: Markdown (return content) and PDF (ReportLab, pure Python)."""

from __future__ import annotations

import html
import logging
import re
from io import BytesIO

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


def _html_blocks_to_flowables_data(html_str: str) -> list[tuple[str, str]]:
    """Extract block-level elements in order: (tag, plain_text)."""
    blocks: list[tuple[str, str]] = []
    # Match <h1>...</h1>, <h2>...</h2>, etc., <p>...</p>, <pre>...</pre>, <li>...</li>
    pattern = re.compile(
        r"<(h[1-4]|p|pre|li)[^>]*>(.*?)</\1>",
        re.DOTALL | re.IGNORECASE,
    )
    for m in pattern.finditer(html_str):
        tag = m.group(1).lower()
        raw = m.group(2)
        text = _strip_tags(raw).strip()
        if text:
            blocks.append((tag, text))
    # If no blocks found (e.g. bare text), treat whole thing as one paragraph
    if not blocks:
        text = _strip_tags(html_str).strip()
        if text:
            blocks.append(("p", text))
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
    for tag, text in blocks:
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
            story.append(Paragraph(f"• {escaped}", body_style))
        else:
            story.append(Paragraph(escaped, body_style))
        story.append(Spacer(1, 4))

    if not story:
        fallback = html.escape(content.replace("\n", "<br/>"))
        story.append(Paragraph(fallback, body_style))

    doc.build(story)
    buf.seek(0)
    return buf.read()
