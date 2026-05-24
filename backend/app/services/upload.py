"""Upload pipeline: extract zip, filter log files, drop them in the Vector watch volume.

Vector picks the files up via inotify and parses + pushes them to Loki. The
backend does not parse log content itself.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.lib.archive import PathTraversalError, extract_zip_safe
from app.lib.config import config

logger = logging.getLogger(__name__)

MAX_COMPRESSED_BYTES = 100 * 1024 * 1024  # 100 MB
MAX_UNCOMPRESSED_BYTES = 500 * 1024 * 1024  # 500 MB

LOG_EXTENSIONS = {".log", ".csv", ".json"}
LOG_EXTENSION_PREFIX = ".log."
LOG_NAMES = {"stdout", "stderr"}

PATH_PREFIXES = ("logs", "log", "data")


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
    """Raise ValueError if compressed size > 100 MB or total uncompressed > 500 MB."""
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
    session_id: str
    error: str | None = None


def _resolve_temp_dir() -> Path:
    return Path(tempfile.gettempdir())


def _safe_path_component(value: str, *, fallback: str) -> str:
    """Sanitize a label into a filesystem-safe path component."""
    out = "".join(c if (c.isalnum() or c in "-._") else "_" for c in (value or ""))
    return out.lstrip(".") or fallback


def _derive_service(rel_path: Path) -> str:
    """Pick a 'service' folder name from the file's path inside the archive.

    Convention: ``<prefix>/<service>/.../<filename>`` where prefix is one of
    ``logs|log|data``. Falls back to "upload" for flat archives. Vector
    re-derives this from its watch path, but we need it here to lay the file
    down under ``<drop>/<session>/<service>/<filename>``.
    """
    parts = [p for p in rel_path.parts if p and p not in (".", "..")]
    if not parts:
        return "upload"
    i = 1 if parts[0].lower() in PATH_PREFIXES else 0
    if i < len(parts) - 1:  # at least one path segment before the filename
        return parts[i]
    return "upload"


def _drop_to_vector_dir(
    file_path: Path, session_id: str, service: str, filename: str
) -> bool:
    """Copy an extracted log file into the Vector sidecar's watch dir.

    Layout: ``<VECTOR_LOG_DROP_DIR>/<session_id>/<service>/<filename>``.
    Returns False when the drop dir isn't configured or the copy fails — failure
    must never block the upload response, but a False return means the file
    won't reach Loki.
    """
    drop_root = config.VECTOR_LOG_DROP_DIR
    if not drop_root:
        return False
    try:
        target_dir = (
            Path(drop_root)
            / _safe_path_component(session_id, fallback="session")
            / _safe_path_component(service, fallback="upload")
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / _safe_path_component(filename, fallback="log")
        shutil.copyfile(file_path, target)
        return True
    except Exception:
        logger.exception(
            "Vector sidecar drop failed (session_id=%s service=%s file=%s)",
            session_id,
            service,
            filename,
        )
        return False


def run_upload_pipeline(zip_path: Path, session_id: str) -> UploadResult:
    """Extract zip, filter log files, drop each into Vector's watch volume."""
    files_processed = 0
    files_skipped = 0

    def _failed(error: str) -> UploadResult:
        return UploadResult(
            status="failed",
            files_processed=files_processed,
            files_skipped=files_skipped,
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
                rel_path = file_path.relative_to(dest)
                service = _derive_service(rel_path)
                if _drop_to_vector_dir(
                    file_path,
                    session_id=session_id,
                    service=service,
                    filename=rel_path.name,
                ):
                    files_processed += 1
                else:
                    files_skipped += 1

        status = "partial" if files_skipped > 0 else "success"
        return UploadResult(
            status=status,
            files_processed=files_processed,
            files_skipped=files_skipped,
            session_id=session_id,
        )
    except (PathTraversalError, ValueError, Exception) as e:
        return _failed(str(e))
