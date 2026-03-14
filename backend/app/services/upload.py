"""Upload pipeline: extract → filter → parse → push to Loki; log file patterns and size checks."""
from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.lib.archive import PathTraversalError, extract_zip_safe
from app.lib.config import config
from app.lib.loki_client import push_logs
from app.lib.prometheus_client import record_metrics
from app.services.labels import derive_labels_from_file_path
from app.services.log_parser import parse_lines
from app.services.metrics import derive_metrics

# Limits per spec (MVP)
MAX_COMPRESSED_BYTES = 100 * 1024 * 1024   # 100 MB
MAX_UNCOMPRESSED_BYTES = 500 * 1024 * 1024  # 500 MB

# Log file patterns: .log, .csv, .json; optional .log.*, stdout, stderr
LOG_EXTENSIONS = {".log", ".csv", ".json"}
LOG_EXTENSION_PREFIX = ".log."
LOG_NAMES = {"stdout", "stderr"}


def is_log_file(path: Path | str) -> bool:
    """True if path matches log file pattern (.log, .csv, .json, .log.*, stdout, stderr)."""
    p = Path(path)
    name = p.name
    suffix = p.suffix.lower()
    if suffix in LOG_EXTENSIONS:
        return True
    if suffix and name.lower().startswith(LOG_EXTENSION_PREFIX):
        return True
    if name.lower() in LOG_NAMES:
        return True
    return False


def filter_log_files(extracted_paths: list[Path]) -> tuple[list[Path], int]:
    """Split into log files and skipped. Returns (log_files, skipped_count)."""
    log_files: list[Path] = []
    for path in extracted_paths:
        if path.is_file() and is_log_file(path):
            log_files.append(path)
    skipped = len(extracted_paths) - len(log_files)
    return log_files, skipped


def check_archive_sizes(zip_path: Path, uncompressed_paths: list[Path]) -> None:
    """
    Raise ValueError if compressed size > 100 MB or total uncompressed > 500 MB.
    """
    compressed = zip_path.stat().st_size
    if compressed > MAX_COMPRESSED_BYTES:
        raise ValueError(
            f"Archive compressed size {compressed} exceeds limit {MAX_COMPRESSED_BYTES} (100 MB)"
        )
    total = sum(p.stat().st_size for p in uncompressed_paths if p.is_file())
    if total > MAX_UNCOMPRESSED_BYTES:
        raise ValueError(
            f"Archive uncompressed size {total} exceeds limit {MAX_UNCOMPRESSED_BYTES} (500 MB)"
        )


@dataclass
class UploadResult:
    """Result of upload pipeline; matches API contract."""

    status: str  # success | partial | failed
    files_processed: int
    files_skipped: int
    lines_parsed: int
    lines_rejected: int
    session_id: str
    error: str | None = None


def _resolve_temp_dir() -> Path:
    """Return DATA_DIR if writable, else system temp dir."""
    try:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        return config.DATA_DIR
    except OSError:
        return Path(tempfile.gettempdir())


def run_upload_pipeline(
    zip_path: Path,
    session_id: str,
    *,
    base_labels: dict[str, str] | None = None,
) -> UploadResult:
    """
    Extract zip, filter log files, parse lines, push to Loki with session_id and labels.
    """
    files_processed = 0
    files_skipped = 0
    lines_parsed = 0
    lines_rejected = 0

    def _failed(error: str) -> UploadResult:
        return UploadResult(
            status="failed",
            files_processed=files_processed,
            files_skipped=files_skipped,
            lines_parsed=lines_parsed,
            lines_rejected=lines_rejected,
            session_id=session_id,
            error=error,
        )

    try:
        if zip_path.stat().st_size > MAX_COMPRESSED_BYTES:
            raise ValueError(
                f"Archive compressed size exceeds limit ({MAX_COMPRESSED_BYTES} bytes / 100 MB)"
            )

        with tempfile.TemporaryDirectory(dir=_resolve_temp_dir(), prefix="upload_") as tmp:
            dest = Path(tmp)
            extracted = extract_zip_safe(zip_path, dest)
            check_archive_sizes(zip_path, extracted)
            log_files, files_skipped = filter_log_files(extracted)

            for file_path in log_files:
                files_processed += 1
                rel_path = file_path.relative_to(dest)
                labels = {**derive_labels_from_file_path(rel_path), "session_id": session_id}
                if base_labels:
                    labels = {**base_labels, **labels}
                labels = {k: str(v) for k, v in labels.items() if v}

                lines = file_path.read_text(errors="replace").splitlines()
                records, rej = parse_lines(lines, source_file=rel_path.as_posix())
                lines_parsed += len(records) - rej
                lines_rejected += rej

                if records:
                    records.sort(key=lambda r: r.timestamp_ns)
                    push_logs([r.to_loki_entry() for r in records], labels)

                    derived = derive_metrics(records)
                    record_metrics(
                        session_id=session_id,
                        service=labels.get("service", "upload"),
                        errors=derived.errors_total,
                        total=derived.requests_total,
                        rate=derived.error_rate,
                        response_times=derived.response_times,
                    )

        status = "partial" if (lines_rejected > 0 or files_skipped > 0) else "success"
        return UploadResult(
            status=status,
            files_processed=files_processed,
            files_skipped=files_skipped,
            lines_parsed=lines_parsed,
            lines_rejected=lines_rejected,
            session_id=session_id,
        )
    except (PathTraversalError, ValueError, Exception) as e:
        return _failed(str(e))
