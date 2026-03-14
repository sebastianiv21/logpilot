"""Log line parser: JSON first, then regex; normalized schema; preserve raw_message."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_TZ_OFFSET_RE = re.compile(r"(\d)\s+([+-]\d{2}:?\d{2})$")

VALID_LEVELS = frozenset({"DEBUG", "INFO", "WARN", "ERROR", "TRACE", "FATAL"})

LEVEL_ALIASES: dict[str, str] = {
    "CRIT": "FATAL",
    "CRITICAL": "FATAL",
    "WARNING": "WARN",
    "LOG": "INFO",
    "NOTICE": "INFO",
    "SEVERE": "ERROR",
}

# Pino / bunyan numeric log levels
NUMERIC_LEVELS: dict[int, str] = {
    10: "TRACE",
    20: "DEBUG",
    30: "INFO",
    40: "WARN",
    50: "ERROR",
    60: "FATAL",
}

_LEVEL_ALT = r"DEBUG|INFO|WARN|WARNING|ERROR|TRACE|FATAL|CRIT|CRITICAL"

LOG_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # ISO-like with level and message (supports . or , for fractional seconds)
    # Matches: "2026-03-13 12:45:43,119 INFO  [io.qua...] msg"
    # Matches: "2026-03-13 12:47:14,484 - root - INFO - msg" (Python logging)
    # Matches: "2026-03-13 12:44:46,145 CRIT msg" (supervisord)
    (
        "iso_level_msg",
        re.compile(
            r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"
            r"(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+"
            r"(?:[-]\s+\S+\s+[-]\s+)?"
            rf"(?P<level>{_LEVEL_ALT})\s+"
            r"[-]?\s*(?P<message>.*)$",
            re.IGNORECASE,
        ),
    ),
    # PostgreSQL: "2026-03-13 12:44:47.213 UTC [1734] LOG:  message"
    (
        "postgres",
        re.compile(
            r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)"
            r"\s+\w+\s+"
            r"\[\d+\]\s+"
            r"(?P<level>\w+):\s+"
            r"(?P<message>.*)$",
        ),
    ),
    # Tab-separated (Temporal after ANSI strip):
    # "2026-03-13T12:44:48.079Z\tINFO\tMessage\t{json}"
    (
        "tab_separated",
        re.compile(
            r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
            r"(?:\.\d+)?Z?)\t"
            r"(?P<level>\w+)\t"
            r"(?P<message>.+)$",
        ),
    ),
    # Bracketed timestamp + level: "[2026-03-13 12:45:23] INFO message"
    (
        "ts_level",
        re.compile(
            r"^(?P<timestamp>\[\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}[.,]?\d*\])\s*"
            rf"(?P<level>{_LEVEL_ALT})[:\s]+"
            r"(?P<message>.*)$",
            re.IGNORECASE,
        ),
    ),
    # Bracketed timestamp + message, no level (Spring Boot / Appsmith backend)
    # "[2026-03-13 12:45:23,753] [main] requestId=... - message"
    (
        "bracketed_ts_msg",
        re.compile(
            r"^(?P<timestamp>\[\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}[.,]?\d*\])\s+"
            r"(?P<message>.+)$",
        ),
    ),
    # RFC3164 / syslog style
    (
        "rfc3164",
        re.compile(
            r"^(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"
            r"(?P<message>.*)$"
        ),
    ),
    # Bare ISO timestamp + message (no level)
    # "2026-03-13T12:44:47.194Z Load environment configuration"
    (
        "iso_msg",
        re.compile(
            r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"
            r"(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+"
            r"(?P<message>.+)$",
        ),
    ),
    # Go default log format: "2026/03/13 12:44:49 message"
    (
        "go_log",
        re.compile(
            r"^(?P<timestamp>\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+"
            r"(?P<message>.+)$",
        ),
    ),
    # Level only at start (no timestamp)
    (
        "level_only",
        re.compile(
            rf"^(?P<level>{_LEVEL_ALT})[:\s]+"
            r"(?P<message>.*)$",
            re.IGNORECASE,
        ),
    ),
]

LEVEL_KEYS = ("level", "log_level", "lvl", "severity", "status")
MESSAGE_KEYS = ("message", "msg", "text", "log", "body")
TIMESTAMP_KEYS = ("timestamp", "time", "@timestamp", "date", "ts")


@dataclass
class ParsedLogRecord:
    """Normalized log record for ingestion."""

    timestamp_ns: int
    log_level: str
    raw_message: str
    message: str
    source_file: str | None = None
    structured: bool = field(default=False, repr=False)

    def to_loki_entry(self) -> tuple[str, str]:
        """Return (timestamp_nanoseconds as str, raw_message) for Loki push."""
        return (str(self.timestamp_ns), self.raw_message)


def _parse_iso_timestamp(ts_str: str) -> int | None:
    """Parse ISO-like or bracket timestamp to nanoseconds since epoch."""
    try:
        s = ts_str.strip().strip("[]").replace(",", ".")
        # Go default log format: "2026/03/13 12:44:49" → normalize to ISO
        if len(s) >= 10 and s[4] == "/" and s[7] == "/":
            s = s[:4] + "-" + s[5:7] + "-" + s[8:]

        normalized = s[:-1] + "+00:00" if s.endswith("Z") else s
        for tz_name in ("UTC", "GMT"):
            suffix = f" {tz_name}"
            if normalized.upper().endswith(suffix):
                normalized = normalized[: -len(suffix)] + "+00:00"
                break
        normalized = _TZ_OFFSET_RE.sub(r"\1\2", normalized)

        try:
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return int(dt.timestamp() * 1_000_000_000)
        except ValueError:
            pass

        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                dt = datetime.strptime(s[:26], fmt).replace(tzinfo=UTC)
                return int(dt.timestamp() * 1_000_000_000)
            except ValueError:
                continue
    except Exception:
        pass
    return None


def _normalize_level(raw_level: str) -> str:
    """Normalize a level string to its canonical form."""
    upper = raw_level.strip().upper()
    mapped = LEVEL_ALIASES.get(upper, upper)
    return mapped if mapped in VALID_LEVELS else "unknown"


def _level_from_json(obj: dict[str, Any]) -> str:
    for key in LEVEL_KEYS:
        if key in obj and obj[key] is not None:
            v = obj[key]
            if isinstance(v, int) and v in NUMERIC_LEVELS:
                return NUMERIC_LEVELS[v]
            return _normalize_level(str(v))
    return "unknown"


def _message_from_json(obj: dict[str, Any], raw: str) -> str:
    for key in MESSAGE_KEYS:
        if key in obj and obj[key] is not None:
            return str(obj[key])
    return raw[:500]


def _timestamp_from_json(obj: dict[str, Any]) -> int | None:
    for key in TIMESTAMP_KEYS:
        if key not in obj or obj[key] is None:
            continue
        v = obj[key]
        if isinstance(v, (int, float)):
            if v > 1e12:
                return int(v * 1_000_000) if v < 1e15 else int(v)
            return int(v * 1_000_000_000)
        if isinstance(v, str):
            ns = _parse_iso_timestamp(v)
            if ns is not None:
                return ns
    return None


def _fallback_ts(default_ts_ns: int | None) -> int:
    return default_ts_ns or int(time.time() * 1_000_000_000)


def parse_line(
    line: str,
    *,
    source_file: str | None = None,
    default_ts_ns: int | None = None,
) -> ParsedLogRecord:
    """
    Parse a single log line into a normalized record.
    Tries JSON first, then regex patterns. Preserves raw_message (ANSI-stripped).
    """
    raw = line.strip()
    if not raw:
        return ParsedLogRecord(
            timestamp_ns=_fallback_ts(default_ts_ns),
            log_level="unknown",
            raw_message="(empty)",
            message="(empty)",
            source_file=source_file,
            structured=True,
        )

    clean = ANSI_RE.sub("", raw)

    try:
        obj = json.loads(clean)
        if isinstance(obj, dict):
            return ParsedLogRecord(
                timestamp_ns=_timestamp_from_json(obj) or _fallback_ts(default_ts_ns),
                log_level=_level_from_json(obj),
                raw_message=clean,
                message=_message_from_json(obj, clean),
                source_file=source_file,
                structured=True,
            )
    except json.JSONDecodeError, TypeError:
        pass

    for _name, pattern in LOG_PATTERNS:
        m = pattern.match(clean)
        if not m:
            continue
        g = m.groupdict()
        ts = _parse_iso_timestamp(g["timestamp"]) if g.get("timestamp") else None
        level = _normalize_level(g.get("level", "unknown"))
        return ParsedLogRecord(
            timestamp_ns=ts or _fallback_ts(default_ts_ns),
            log_level=level,
            raw_message=clean,
            message=(g.get("message") or clean).strip(),
            source_file=source_file,
            structured=True,
        )

    return ParsedLogRecord(
        timestamp_ns=_fallback_ts(default_ts_ns),
        log_level="unknown",
        raw_message=clean,
        message=clean[:500],
        source_file=source_file,
    )


_CONTINUATION_RE = re.compile(
    r"^(?:"
    r"\s*at\s"  # stack trace ("at ..." or "    at ...")
    r"|[\s\t]+"  # indented continuation
    r"|[}\])]"  # closing brace/bracket
    r"|Caused by[:\s]"  # Java chained exceptions
    r")"
)

_STARTS_NEW_ENTRY_RE = re.compile(
    r"^(?:"
    r"\d{4}[-/]\d{2}[-/]\d{2}"  # ISO or Go timestamp start
    r"|\[\d{4}[-/]"  # bracketed timestamp "[2026-..."
    r"|\w{3}\s+\d{1,2}\s+\d{2}:"  # RFC3164
    r"|\{\""  # JSON object (opening brace + quote)
    rf"|(?:{_LEVEL_ALT})[\s:]"  # bare level prefix
    r")",
    re.IGNORECASE,
)


def _is_continuation(clean: str) -> bool:
    """True if the line looks like a continuation of a previous multi-line log entry."""
    if _CONTINUATION_RE.match(clean):
        return True
    if not _STARTS_NEW_ENTRY_RE.match(clean):
        return True
    return False


def parse_lines(
    lines: list[str],
    *,
    source_file: str | None = None,
) -> tuple[list[ParsedLogRecord], int]:
    """
    Parse multiple lines with multi-line folding. Returns (parsed_records, rejected_count).

    Continuation lines (stack traces, indented text, lines without a leading
    timestamp/level) are folded into the preceding structured record rather than
    being emitted as separate rejected entries.

    Rejected = unstructured lines that couldn't be folded; still ingested with
    ingest timestamp.
    """
    base_ts = int(time.time() * 1_000_000_000)
    parsed: list[ParsedLogRecord] = []
    rejected = 0

    prev_structured: ParsedLogRecord | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        clean = ANSI_RE.sub("", stripped)

        if not clean:
            continue

        raw_for_cont = ANSI_RE.sub("", line.rstrip())
        if prev_structured is not None and _is_continuation(raw_for_cont):
            prev_structured.raw_message += "\n" + clean
            prev_structured.message += "\n" + clean
            continue

        record = parse_line(line, source_file=source_file, default_ts_ns=base_ts + i)
        parsed.append(record)
        if record.structured:
            prev_structured = record
        else:
            rejected += 1

    return parsed, rejected
