"""One-time backfill: index every existing report into incident memory.

Walks every session, fetches its reports, and indexes the ones with non-empty
content via ``incident_memory.index_existing_report_content``. Idempotent —
re-running upserts the same chunks and overwrites prior backfill output for
each report.

Usage::

    cd backend
    uv run python -m scripts.backfill_report_embeddings           # all sessions
    uv run python -m scripts.backfill_report_embeddings --dry-run # report only

Requires the same environment as the FastAPI app: DATABASE_URL, LLM_API_KEY,
LLM_BASE_URL, EMBEDDING_MODEL.
"""

from __future__ import annotations

import argparse
import logging
import sys

from app.lib.db import close_pool, init_pool, initialize_schema
from app.lib.repositories import ReportRepository, SessionRepository
from app.services.incident_memory import index_existing_report_content

logger = logging.getLogger(__name__)


def run(*, dry_run: bool) -> int:
    """Return the number of reports indexed (or that would be, in dry-run)."""
    sessions = SessionRepository().list_all()
    report_repo = ReportRepository()

    total_reports = 0
    indexed = 0
    skipped_empty = 0
    failed = 0

    for session in sessions:
        for report in report_repo.list_by_session(session.id):
            total_reports += 1
            if not (report.content or "").strip():
                skipped_empty += 1
                continue
            if dry_run:
                indexed += 1
                continue
            ok = index_existing_report_content(
                session_id=session.id,
                report_id=report.id,
                question=report.question or "",
                created_at=report.created_at,
                content=report.content,
            )
            if ok:
                indexed += 1
            else:
                failed += 1

    logger.info(
        "Backfill complete: sessions=%d reports_total=%d indexed=%d "
        "skipped_empty=%d failed=%d dry_run=%s",
        len(sessions),
        total_reports,
        indexed,
        skipped_empty,
        failed,
        dry_run,
    )
    return indexed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count reports that would be indexed but make no changes.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Per-report log lines."
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s %(message)s",
    )

    initialize_schema()
    init_pool()
    try:
        run(dry_run=args.dry_run)
    finally:
        close_pool()
    return 0


if __name__ == "__main__":
    sys.exit(main())
