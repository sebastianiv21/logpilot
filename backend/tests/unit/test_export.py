"""Unit tests for report export helpers."""

from __future__ import annotations

import pytest

from app.services.export import export_markdown, export_pdf


EXPORT_FIXTURES = [
    """## Incident Summary
Short report.

## Coding agent fix prompt
Use the evidence before changing code.

## Next troubleshooting steps
1. Check logs.
2. Compare latency.
""",
    """## Incident Summary
Question context:
`Why did checkout requests start timing out after the deploy with the new routing layer and fallback retry logic enabled for all tenants?`

## Supporting Evidence
```text
TimeoutError: request exceeded 30s
retry_count=5 downstream=inventory
```

## Coding agent fix prompt
Adjust the retry policy in `backend/app/services/agent.py` and preserve uncertainty about downstream saturation.

## Next troubleshooting steps
1. Compare retry counts before and after the deploy.
2. Sample slow traces for the inventory dependency.
""",
    """## Incident Summary
Mixed prose and code blocks.

## Uncertainty
Need to confirm whether one noisy tenant drove the whole spike.

## Coding agent fix prompt
Prepare a minimal code change prompt that references the uncertainty and supporting evidence, and avoid claiming certainty about tenant isolation.

## Next troubleshooting steps
1. Query logs by tenant.
2. Review the throttling code path.
""",
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
