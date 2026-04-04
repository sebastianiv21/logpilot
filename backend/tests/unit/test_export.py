"""Unit tests for report export helpers."""

from __future__ import annotations

import gc

import pytest
from app.services.export import (
    MAX_PDF_CODE_LINES,
    PDFExportTooLargeError,
    export_markdown,
    export_pdf,
    export_pdf_to_file,
    get_process_maxrss_kb,
)

LONG_X = "x" * 240
LONG_Y = "y" * 240

EXPORT_FIXTURES = [
    """## Incident Summary
Short report.

## Coding agent fix prompt
Use the evidence before changing code.

## Next troubleshooting steps
1. Check logs.
2. Compare latency.
""",
    (
        "## Incident Summary\n"
        "Question context:\n"
        "`Why did checkout requests start timing out after the deploy with the new routing "
        "layer and fallback retry logic enabled?`\n\n"
        "## Supporting Evidence\n"
        "```text\n"
        "TimeoutError: request exceeded 30s\n"
        "retry_count=5 downstream=inventory\n"
        "```\n\n"
        "## Coding agent fix prompt\n"
        "Adjust the retry policy in `backend/app/services/agent.py` and preserve uncertainty "
        "about downstream saturation.\n\n"
        "## Next troubleshooting steps\n"
        "1. Compare retry counts before and after the deploy.\n"
        "2. Sample slow traces for the inventory dependency.\n"
    ),
    (
        "## Incident Summary\n"
        "Mixed prose and code blocks.\n\n"
        "## Uncertainty\n"
        "Need to confirm whether one noisy tenant drove the whole spike.\n\n"
        "## Coding agent fix prompt\n"
        "Prepare a minimal code change prompt that references the uncertainty and "
        "supporting evidence.\n\n"
        "## Next troubleshooting steps\n"
        "1. Query logs by tenant.\n"
        "2. Review the throttling code path.\n"
    ),
]

SMALL_REPORT_FIXTURES = [
    (
        "## Incident Summary\n"
        "Checkout requests timed out for a subset of tenants after the deploy.\n\n"
        "## Supporting Evidence\n"
        "```python\n"
        "def handle_retry(request_id: str, retries: int) -> None:\n"
        "    if retries > 5:\n"
        "        raise TimeoutError(\n"
        '            f"request {request_id} exceeded timeout after rollout"\n'
        "        )\n"
        "```\n\n"
        "## Coding agent fix prompt\n"
        "Review the retry threshold and preserve uncertainty about downstream saturation.\n"
    ),
    (
        "## Incident Summary\n"
        "The report is short, but the supporting evidence has long unbroken lines.\n\n"
        "## Supporting Evidence\n"
        "```text\n"
        f"trace_id=abc123 tenant=checkout latency_ms=30123 note={LONG_X}\n"
        f"trace_id=def456 tenant=checkout latency_ms=30210 note={LONG_Y}\n"
        "```\n\n"
        "## Next troubleshooting steps\n"
        "1. Compare latency before and after the rollout.\n"
        "2. Inspect retry amplification by tenant.\n\n"
        "## Coding agent fix prompt\n"
        "Adjust timeout handling without assuming the downstream service is definitively "
        "at fault.\n"
    ),
    (
        "## Incident Summary\n"
        "Two to three page report with prose, list items, and a moderate stack trace.\n\n"
        "## Supporting Evidence\n"
        "- `checkout-api` started timing out after the deploy.\n"
        "- Retry counts increased from `1` to `5`.\n"
        "- Tenants with the new flag saw the steepest regression.\n\n"
        "```text\n"
        "Traceback (most recent call last):\n"
        '  File "/srv/app/checkout.py", line 48, in submit_order\n'
        "    return inventory.reserve(item_id, tenant_id=tenant_id)\n"
        '  File "/srv/app/inventory.py", line 91, in reserve\n'
        '    raise TimeoutError("inventory reserve exceeded 30s")\n'
        "TimeoutError: inventory reserve exceeded 30s\n"
        "```\n\n"
        "## Coding agent fix prompt\n"
        "Investigate the routing change and retry policy while preserving uncertainty.\n"
    ),
]


def test_export_markdown_preserves_coding_agent_fix_prompt() -> None:
    content = EXPORT_FIXTURES[0]

    exported = export_markdown(content)

    assert exported.endswith("\n")
    assert "## Coding agent fix prompt" in exported
    assert "1. Check logs." in exported


@pytest.mark.parametrize("content", EXPORT_FIXTURES)
def test_export_pdf_handles_representative_report_fixtures(content: str) -> None:
    pdf_bytes = export_pdf(content)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 800


@pytest.mark.parametrize("content", SMALL_REPORT_FIXTURES)
def test_export_pdf_handles_small_realistic_reports(content: str) -> None:
    pdf_bytes = export_pdf(content)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000


def test_export_pdf_repeated_small_report_memory_is_bounded() -> None:
    content = SMALL_REPORT_FIXTURES[2]
    rss_before = get_process_maxrss_kb()

    for i in range(60):
        pdf_bytes = export_pdf(content)
        assert pdf_bytes.startswith(b"%PDF")
        if i % 15 == 0:
            gc.collect()

    gc.collect()
    rss_after = get_process_maxrss_kb()

    assert rss_after - rss_before < 16 * 1024


def test_export_pdf_rejects_extreme_code_block_reports() -> None:
    code = "\n".join(
        f"frame {i}: retry_count=5 timeout=true"
        for i in range(MAX_PDF_CODE_LINES + 50)
    )
    content = (
        "## Incident Summary\nThe report is too code-heavy for PDF export.\n\n"
        "## Supporting Evidence\n```text\n"
        f"{code}\n"
        "```\n\n## Coding agent fix prompt\nUse Markdown export instead.\n"
    )

    with pytest.raises(PDFExportTooLargeError):
        export_pdf_to_file(content)
