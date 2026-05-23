"""On-demand source-code search via ripgrep, with allowlisted file reads.

Replaces the previous embedding-based search_repo: for incident investigation
the agent has concrete clues from logs (error strings, function names, paths)
and wants literal lookups rather than fuzzy semantic similarity.

Two tools:
  grep_repo(pattern, ...) -> list[GrepHit]
  read_file(path, ...)    -> FileSlice

Both operate only under the directories listed in config.knowledge_code_sources;
attempts to read outside that allowlist raise OutsideAllowlistError.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from app.lib.config import config

logger = logging.getLogger(__name__)

GREP_RESULTS_MAX = 200
GREP_DEFAULT_LIMIT = 50
GREP_TIMEOUT_SECONDS = 10
READ_MAX_LINES = 2000


class OutsideAllowlistError(ValueError):
    """Raised when a path resolves outside every configured code-search root."""


class RipgrepUnavailableError(RuntimeError):
    """Raised when the ripgrep binary cannot be found at runtime."""


@dataclass
class GrepHit:
    path: str
    line: int
    snippet: str
    before: list[str] = field(default_factory=list)
    after: list[str] = field(default_factory=list)


@dataclass
class FileSlice:
    path: str
    line_start: int
    line_end: int
    total_lines: int
    content: str
    truncated: bool


def _allowlist_roots() -> list[Path]:
    """Resolved absolute paths of every configured code-search root that exists."""
    roots: list[Path] = []
    for raw in config.knowledge_code_sources:
        try:
            resolved = Path(raw).resolve()
        except OSError:
            continue
        if resolved.exists() and resolved.is_dir():
            roots.append(resolved)
    return roots


def _resolve_under_allowlist(path: str | Path) -> Path:
    """Resolve `path` and verify it lives under an allowlist root.

    Accepts absolute paths or paths relative to one of the roots. Raises
    OutsideAllowlistError if no root contains the resolved target.
    """
    roots = _allowlist_roots()
    if not roots:
        raise OutsideAllowlistError("No KNOWLEDGE_CODE_SOURCES configured")
    candidate = Path(path)
    candidates: list[Path] = []
    if candidate.is_absolute():
        candidates.append(candidate)
    else:
        candidates.extend(root / candidate for root in roots)
    for c in candidates:
        try:
            resolved = c.resolve()
        except OSError:
            continue
        for root in roots:
            if resolved == root or resolved.is_relative_to(root):
                return resolved
    raise OutsideAllowlistError(f"Path resolves outside allowlist: {path!r}")


def _ripgrep_binary() -> str:
    path = shutil.which("rg")
    if not path:
        raise RipgrepUnavailableError(
            "ripgrep ('rg') not found on PATH; install it in the backend image"
        )
    return path


def grep_repo(
    pattern: str,
    *,
    glob: str | None = None,
    max_results: int = GREP_DEFAULT_LIMIT,
    context_lines: int = 2,
) -> list[GrepHit]:
    """Search every configured code root for `pattern` (ripgrep regex).

    Returns at most `max_results` hits, capped at GREP_RESULTS_MAX. Each hit
    carries the file path (relative to its allowlist root), 1-based line
    number, the matching line, and up to `context_lines` of before/after.
    Returns an empty list if no roots are configured.
    """
    if not pattern.strip():
        return []
    limit = max(1, min(max_results, GREP_RESULTS_MAX))
    context_lines = max(0, min(context_lines, 10))

    roots = _allowlist_roots()
    if not roots:
        logger.info("grep_repo called with no KNOWLEDGE_CODE_SOURCES configured")
        return []

    rg = _ripgrep_binary()
    args: list[str] = [
        rg,
        "--json",
        "--no-ignore-vcs",
        "--hidden",
        "--max-count",
        str(limit),
        "--max-filesize",
        "2M",
    ]
    if context_lines:
        args += ["--context", str(context_lines)]
    if glob:
        args += ["--glob", glob]
    args.append(pattern)
    args += [str(root) for root in roots]

    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=GREP_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        logger.warning("grep_repo timeout for pattern=%r", pattern)
        return []

    # rg exits 1 when there are no matches; treat any other non-zero as a soft error.
    if proc.returncode not in (0, 1):
        logger.warning("ripgrep exit=%s stderr=%s", proc.returncode, proc.stderr[:500])
        return []

    return _parse_rg_json(proc.stdout, roots, limit)


def _parse_rg_json(stdout: str, roots: list[Path], limit: int) -> list[GrepHit]:
    hits: list[GrepHit] = []
    pending_before: dict[str, list[str]] = {}
    last_match_by_file: dict[str, GrepHit] = {}

    for raw_line in stdout.splitlines():
        if not raw_line:
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        etype = event.get("type")
        data = event.get("data", {})
        if etype not in {"match", "context"}:
            continue
        path_text = data.get("path", {}).get("text")
        if not path_text:
            continue
        rel = _relativize(Path(path_text), roots)
        text = (data.get("lines", {}) or {}).get("text", "").rstrip("\n")
        line_no = int(data.get("line_number") or 0)

        if etype == "match":
            hit = GrepHit(
                path=rel,
                line=line_no,
                snippet=text,
                before=pending_before.pop(rel, []),
            )
            hits.append(hit)
            last_match_by_file[rel] = hit
            if len(hits) >= limit:
                break
        else:  # context
            prior = last_match_by_file.get(rel)
            if prior and line_no > prior.line:
                prior.after.append(text)
            else:
                pending_before.setdefault(rel, []).append(text)

    return hits


def _relativize(target: Path, roots: list[Path]) -> str:
    """Return target relative to the longest matching allowlist root, else absolute."""
    best: tuple[int, str] | None = None
    for root in roots:
        try:
            rel = target.resolve().relative_to(root)
        except ValueError:
            continue
        rel_str = str(rel)
        if best is None or len(str(root)) > best[0]:
            best = (len(str(root)), rel_str)
    return best[1] if best else str(target)


def read_file(
    path: str,
    *,
    line_start: int = 1,
    line_end: int | None = None,
) -> FileSlice:
    """Read a bounded slice of a file under the allowlist.

    line_start is 1-based, line_end inclusive. The total returned lines is
    capped at READ_MAX_LINES; the response indicates whether truncation
    occurred. Raises OutsideAllowlistError for paths outside the allowlist.
    """
    resolved = _resolve_under_allowlist(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"Not a file: {path!r}")

    raw = resolved.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    total = len(lines)

    start = max(1, line_start)
    end = total if line_end is None else min(line_end, total)
    if end < start:
        end = start

    requested = end - start + 1
    truncated = requested > READ_MAX_LINES
    if truncated:
        end = start + READ_MAX_LINES - 1

    selected = lines[start - 1 : end]
    rel = _relativize(resolved, _allowlist_roots())
    return FileSlice(
        path=rel,
        line_start=start,
        line_end=end,
        total_lines=total,
        content="\n".join(selected),
        truncated=truncated,
    )
