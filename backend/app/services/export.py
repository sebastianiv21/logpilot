"""Report export: Markdown (return content) and PDF (weasyprint)."""

from __future__ import annotations

import logging
from io import BytesIO

import markdown

logger = logging.getLogger(__name__)

_weasyprint_available: bool | None = None


def _check_weasyprint() -> bool:
    global _weasyprint_available
    if _weasyprint_available is not None:
        return _weasyprint_available
    try:
        from weasyprint import HTML  # noqa: F401
        _weasyprint_available = True
    except Exception as e:
        logger.warning("WeasyPrint not available for PDF export: %s", e)
        _weasyprint_available = False
    return _weasyprint_available


def export_markdown(content: str) -> str:
    """Return report content as Markdown (passthrough)."""
    return content


def export_pdf(content: str) -> bytes:
    """Render report Markdown to PDF using weasyprint. Raises if weasyprint unavailable."""
    if not _check_weasyprint():
        raise RuntimeError("PDF export unavailable: WeasyPrint not installed or failed to load")
    from weasyprint import HTML
    html_str = markdown.markdown(content, extensions=["extra"])
    # Wrap in a minimal document for weasyprint
    body_style = (
        "font-family:system-ui,sans-serif;line-height:1.5;"
        "max-width:800px;margin:1em auto;padding:1em"
    )
    doc = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/><title>Report</title></head>
<body style="{body_style}">
{html_str}
</body>
</html>"""
    buf = BytesIO()
    HTML(string=doc).write_pdf(buf)
    return buf.getvalue()
