"""Service/environment/filename label derivation from archive path."""

from __future__ import annotations

from pathlib import Path

PATH_PREFIXES = ("logs", "log", "data")


def derive_labels_from_path(archive_path: Path | str) -> dict[str, str]:
    """
    Derive service, environment, and filename labels from a file path inside an archive.

    Convention: ``<prefix>/<service>/[<env>/...]<filename>``

    * First segment after a known prefix (logs, log, data) → ``service``
    * Intermediate segments between service and filename → ``environment``
    * Last segment (the actual file) → ``filename``

    If the structure is flat or unrecognised, falls back to ``service=upload``.
    """
    path = Path(archive_path)
    parts = [p for p in path.parts if p and p not in (".", "..")]
    if not parts:
        return {"service": "upload", "environment": "unknown"}

    i = 0
    if parts[0].lower() in PATH_PREFIXES:
        i = 1

    service = "upload"
    environment = "unknown"
    filename = ""

    if i < len(parts):
        service = parts[i]
        remaining = parts[i + 1 :]
        if remaining:
            filename = remaining[-1]
            env_parts = remaining[:-1]
            if env_parts:
                environment = "/".join(env_parts)
    else:
        base = path.stem
        if base and base != ".":
            service = base

    labels: dict[str, str] = {"service": service, "environment": environment}
    if filename:
        labels["filename"] = filename
    return labels


def derive_labels_from_file_path(file_path_in_archive: Path | str) -> dict[str, str]:
    """
    Same as ``derive_labels_from_path`` but named for clarity when called
    per-file inside an archive (e.g. ``logs/backend/app.log``).
    """
    return derive_labels_from_path(file_path_in_archive)
