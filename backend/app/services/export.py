"""Report export: Markdown (return content) and PDF (ReportLab, pure Python)."""

from __future__ import annotations

import html
import re
import resource
import sys
import tempfile
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import BinaryIO, Literal

import markdown
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

MAX_PDF_REPORT_CHARS = 400_000
MAX_PDF_BLOCKS = 2_500
MAX_PDF_CODE_LINES = 4_000
PDF_EXPORT_SPOOL_MAX_SIZE = 512 * 1024
PDF_STREAM_CHUNK_SIZE = 64 * 1024
MAX_PARAGRAPH_CHARS = 12_000
MAX_CODE_LINE_LENGTH = 240


def _sanitize_markdown_content(content: str) -> str:
    """Normalize line endings and strip characters that commonly break PDF generation."""
    return content.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "").strip()


def export_markdown(content: str) -> str:
    """Return report content as Markdown with consistent formatting for viewers."""
    if not content or not content.strip():
        return ""
    content = _sanitize_markdown_content(content)
    normalized = re.sub(r"\n{3,}", "\n\n", content)
    return normalized + "\n"


def _strip_tags(html_fragment: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", html_fragment)
    text = re.sub(r"\s+", " ", text).strip()
    return html.unescape(text)


BlockItem = tuple[
    str, str, Literal["ol", "ul"] | None, int | None, str | None
]  # tag, text, list_type, ol_index, raw_html (for p and li)


@dataclass(slots=True)
class PDFExportStats:
    report_chars: int
    code_fence_count: int
    code_block_line_count: int
    block_count: int = 0
    flowable_count: int = 0
    output_bytes: int = 0
    duration_ms: float = 0.0
    rss_kb_before: int = 0
    rss_kb_after: int = 0


@dataclass(slots=True)
class PDFExportResult:
    file: BinaryIO
    stats: PDFExportStats


class PDFExportTooLargeError(ValueError):
    """Raised when a report exceeds defensive PDF export limits."""

    def __init__(self, detail: str, stats: PDFExportStats) -> None:
        super().__init__(detail)
        self.detail = detail
        self.stats = stats


class PDFExportRenderError(RuntimeError):
    """Raised when PDF rendering fails after stats collection begins."""

    def __init__(self, stats: PDFExportStats) -> None:
        super().__init__("PDF export failed")
        self.stats = stats


class _ReportHTMLParser(HTMLParser):
    """Parse Markdown HTML into block items with list context and raw paragraph HTML."""

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
        if self._current_tag in ("p", "li"):
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
            raw_html = (
                "".join(self._current_raw).strip()
                if self._current_tag in ("p", "li")
                else None
            )
            if text:
                list_type: Literal["ol", "ul"] | None = (
                    self._list_stack[-1] if self._list_stack else None
                )
                index: int | None = self._ol_index if list_type == "ol" else None
                self.blocks.append((self._current_tag, text, list_type, index, raw_html))
            self._current_tag = None
            self._current_text = []
            self._current_raw = []
        elif self._current_tag in ("p", "li"):
            self._current_raw.append(f"</{tag_l}>")

    def handle_data(self, data: str) -> None:
        if self._current_tag is not None:
            self._current_text.append(data)
            if self._current_tag in ("p", "li"):
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


_PRE_WRAP_SPLIT_CHARS = frozenset(" :.,;/-\\()[]{}=<>")


def _normalize_maxrss_to_kb(raw_value: int | float) -> int:
    """Normalize platform-specific ru_maxrss output to KiB."""
    if sys.platform == "darwin":
        return int(raw_value / 1024)
    return int(raw_value)


def get_process_maxrss_kb() -> int:
    """Return process max RSS in KiB."""
    return _normalize_maxrss_to_kb(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def inspect_pdf_export(content: str) -> PDFExportStats:
    """Collect lightweight stats from Markdown before rendering."""
    normalized = _sanitize_markdown_content(content)
    code_fence_count = 0
    code_block_line_count = 0
    fence_marker: str | None = None
    for line in normalized.splitlines():
        stripped = line.lstrip()
        if fence_marker is None:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence_marker = stripped[:3]
                code_fence_count += 1
        elif stripped.startswith(fence_marker):
            fence_marker = None
        else:
            code_block_line_count += 1
    return PDFExportStats(
        report_chars=len(normalized),
        code_fence_count=code_fence_count,
        code_block_line_count=code_block_line_count,
    )


def _enforce_pdf_guardrails(stats: PDFExportStats) -> None:
    if stats.report_chars > MAX_PDF_REPORT_CHARS:
        raise PDFExportTooLargeError(
            "PDF export is unavailable for very large reports. Use Markdown export instead.",
            stats,
        )
    if stats.code_block_line_count > MAX_PDF_CODE_LINES:
        raise PDFExportTooLargeError(
            "PDF export is unavailable for reports with very large code blocks. "
            "Use Markdown export instead.",
            stats,
        )
    if stats.block_count > MAX_PDF_BLOCKS:
        raise PDFExportTooLargeError(
            "PDF export is unavailable for reports with too many rendered sections. "
            "Use Markdown export instead.",
            stats,
        )


def _wrap_pre_lines(text: str, max_len: int = 78) -> str:
    """Wrap long code lines to avoid expensive ReportLab overflow handling."""
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
            break_at = -1
            for i in range(len(chunk) - 1, -1, -1):
                if chunk[i] in _PRE_WRAP_SPLIT_CHARS:
                    break_at = i
                    break
            if break_at >= 0:
                out.append(chunk[: break_at + 1].rstrip())
                pos += break_at + 1
                while pos < len(line) and line[pos] == " ":
                    pos += 1
            else:
                out.append(chunk)
                pos += max_len
    return "\n".join(out)


def _normalize_preformatted_text(text: str) -> str:
    """Defensively normalize code block content for small pathological inputs."""
    normalized_lines: list[str] = []
    for raw_line in html.unescape(text).splitlines():
        line = raw_line.replace("\t", "    ")
        if len(line) > MAX_CODE_LINE_LENGTH:
            line = _wrap_pre_lines(line, max_len=MAX_CODE_LINE_LENGTH)
            normalized_lines.extend(line.splitlines())
            continue
        normalized_lines.append(line)
    return _wrap_pre_lines("\n".join(normalized_lines), max_len=78)


def _paragraph_to_reportlab_markup(raw_html: str | None, plain_text: str) -> str:
    """Convert paragraph HTML to ReportLab Paragraph markup; preserve <code> as Courier font."""
    if not raw_html or "<code>" not in raw_html:
        return html.escape(plain_text[:MAX_PARAGRAPH_CHARS])
    result: list[str] = []
    i = 0
    raw_html = raw_html[:MAX_PARAGRAPH_CHARS]
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


def _build_story(blocks: list[BlockItem]) -> tuple[list, int]:
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

    def h2_divider() -> Table:
        table = Table([[""]], colWidths=[6.5 * inch], rowHeights=[3])
        table.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.grey)]))
        table.keepWithNext = True
        return table

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
        wordWrap="CJK",
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

    story: list = [Spacer(1, 0.2 * inch)]
    flowable_count = 1
    for tag, text, list_type, ol_index, raw_html in blocks:
        escaped = html.escape(text[:MAX_PARAGRAPH_CHARS])
        if tag == "h1":
            story.append(Paragraph(escaped, title_style))
            flowable_count += 1
        elif tag == "h2":
            story.append(Paragraph(escaped, h2_style))
            story.append(h2_divider())
            flowable_count += 2
        elif tag in ("h3", "h4"):
            story.append(Paragraph(escaped, h3_style))
            flowable_count += 1
        elif tag == "pre":
            pre_text = _normalize_preformatted_text(text)
            story.append(Preformatted(pre_text, code_style))
            flowable_count += 1
        elif tag == "li":
            if raw_html and "<code>" in raw_html:
                li_markup = _paragraph_to_reportlab_markup(raw_html, text)
                prefix = f"{ol_index}. " if list_type == "ol" and ol_index is not None else "• "
                story.append(Paragraph(prefix + li_markup, body_style))
            elif list_type == "ol" and ol_index is not None:
                story.append(Paragraph(f"{ol_index}. {escaped}", body_style))
            else:
                story.append(Paragraph(f"• {escaped}", body_style))
            flowable_count += 1
        elif tag == "p":
            story.append(Paragraph(_paragraph_to_reportlab_markup(raw_html, text), body_style))
            flowable_count += 1
        else:
            story.append(Paragraph(escaped, body_style))
            flowable_count += 1
        spacer_pt = 2 if tag == "li" else 6
        story.append(Spacer(1, spacer_pt))
        flowable_count += 1
    return story, flowable_count


def export_pdf_to_file(content: str) -> PDFExportResult:
    """Render report Markdown to a spooled PDF file for streaming responses."""
    content = _sanitize_markdown_content(content)
    stats = inspect_pdf_export(content)
    stats.rss_kb_before = get_process_maxrss_kb()
    started_at = time.perf_counter()
    file_obj: BinaryIO | None = None
    try:
        _enforce_pdf_guardrails(stats)
        html_str = markdown.markdown(content, extensions=["extra", "sane_lists"])
        blocks = _html_blocks_to_flowables_data(html_str)
        stats.block_count = len(blocks)
        _enforce_pdf_guardrails(stats)

        file_obj = tempfile.SpooledTemporaryFile(max_size=PDF_EXPORT_SPOOL_MAX_SIZE, mode="w+b")
        doc = SimpleDocTemplate(
            file_obj,
            pagesize=(8.5 * inch, 11 * inch),
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=0.75 * inch,
        )
        story, flowable_count = _build_story(blocks)
        stats.flowable_count = flowable_count
        if flowable_count <= 1:
            fallback = html.escape(content.replace("\n", "<br/>"))
            styles = getSampleStyleSheet()
            body_style = ParagraphStyle(
                "ReportBodyFallback",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=12,
                spaceAfter=6,
                wordWrap="CJK",
            )
            story.append(Paragraph(fallback, body_style))
            stats.flowable_count += 1

        doc.build(story, onFirstPage=_pdf_footer_first, onLaterPages=_pdf_footer_later)
        file_obj.seek(0, 2)
        stats.output_bytes = file_obj.tell()
        file_obj.seek(0)
        stats.duration_ms = (time.perf_counter() - started_at) * 1000
        stats.rss_kb_after = get_process_maxrss_kb()
        return PDFExportResult(file=file_obj, stats=stats)
    except PDFExportTooLargeError:
        stats.duration_ms = (time.perf_counter() - started_at) * 1000
        stats.rss_kb_after = get_process_maxrss_kb()
        if file_obj is not None:
            file_obj.close()
        raise
    except Exception as exc:
        stats.duration_ms = (time.perf_counter() - started_at) * 1000
        stats.rss_kb_after = get_process_maxrss_kb()
        if file_obj is not None:
            file_obj.close()
        raise PDFExportRenderError(stats) from exc


def export_pdf(content: str) -> bytes:
    """Render report Markdown to PDF bytes."""
    result = export_pdf_to_file(content)
    try:
        return result.file.read()
    finally:
        result.file.close()


def iter_pdf_chunks(file_obj: BinaryIO, chunk_size: int = PDF_STREAM_CHUNK_SIZE):
    """Yield PDF file chunks for streaming responses."""
    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        yield chunk
