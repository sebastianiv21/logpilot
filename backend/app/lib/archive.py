"""Safe zip extraction with path traversal validation."""

from __future__ import annotations

import zipfile
from pathlib import Path


class PathTraversalError(Exception):
    """Raised when an archive entry would extract outside the target directory."""

    def __init__(self, entry_name: str) -> None:
        self.entry_name = entry_name
        super().__init__(f"Path traversal not allowed: {entry_name!r}")


def extract_zip_safe(
    zip_path: Path | str,
    dest_dir: Path | str,
    *,
    reject_traversal: bool = True,
) -> list[Path]:
    """
    Extract a zip archive into dest_dir with path traversal validation.

    For each entry, the extraction path is resolved and checked to be under dest_dir
    using pathlib.Path.resolve() and is_relative_to(). Entries that would escape
    raise PathTraversalError when reject_traversal is True; otherwise they are skipped.

    Returns the list of extracted file paths (under dest_dir). Directories are
    created but not included in the returned list; only files are.
    """
    dest = Path(dest_dir).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            # Normalize: no leading slashes, forward slashes only
            name = info.filename.replace("\\", "/").lstrip("/")
            if not name:
                continue
            target = (dest / name).resolve()
            if not target.is_relative_to(dest):
                if reject_traversal:
                    raise PathTraversalError(info.filename)
                continue
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src:
                    target.write_bytes(src.read())
                extracted.append(target)

    return extracted
