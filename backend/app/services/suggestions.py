"""Per-session question suggestions.

After log upload, the UI surfaces three pill-shaped suggested questions so
users have an easy starting point for incident investigation. A small
PydanticAI agent reads a bounded sample of the session's logs and returns a
structured ``SuggestedQuestions`` with exactly three items: one general
context question and two anchored on concrete tokens from the sample.

Results are cached per-session in an in-process dict. Uploads to a session
are append-only / reject-on-second (see ``app/api/upload.py``), so the cache
key is stable across the session's lifetime. The cache is intentionally
not persisted: if the process restarts, the next request just recomputes.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from app.lib.config import config
from app.services import agent_tools
from app.services.agent import _build_model  # reuse the OpenAI-compatible model wiring

logger = logging.getLogger(__name__)

LOG_SAMPLE_LIMIT = 60
SUGGESTION_COUNT = 3


class SuggestedQuestions(BaseModel):
    """Exactly three investigation questions for a session."""

    questions: list[str] = Field(
        ...,
        min_length=SUGGESTION_COUNT,
        max_length=SUGGESTION_COUNT,
        description=(
            "Three short questions an operator might ask to investigate this "
            "session. Each must be self-contained, end with a question mark, "
            "and stay under ~120 characters."
        ),
    )


SUGGESTION_INSTRUCTIONS = f"""You suggest incident investigation questions for an operator.

You will be given a sample of log lines from one session. Return exactly
{SUGGESTION_COUNT} short questions that the operator could plausibly ask to
investigate this session.

Guidance:
- Question 1: a general framing question (e.g. "What's the most common error in
  this session?", "Are there signs of upstream timeouts?"). Should work even if
  the log sample is sparse.
- Questions 2 and 3: anchored on concrete tokens from the sample — specific
  service names, error classes, status codes, stack frames. They should feel
  like questions an engineer who actually skimmed these logs would write.
- Keep each question under ~120 characters, ending with a question mark.
- Phrase as questions, not statements or commands. No "investigate X" — say
  "Why does X happen?" or "What caused X?".
- Do NOT include log timestamps, raw IDs, or quoted log lines in the questions.
"""


# Cache: session_id -> list of three questions. Guarded by a lock so a slow
# first request doesn't trigger concurrent agent runs for the same session.
_cache: dict[str, list[str]] = {}
_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _get_session_lock(session_id: str) -> threading.Lock:
    """Per-session reentrant-safe lock so the first slow request blocks
    concurrent readers and only one agent run happens per session."""
    with _locks_guard:
        lock = _locks.get(session_id)
        if lock is None:
            lock = threading.Lock()
            _locks[session_id] = lock
        return lock


def _fetch_log_sample(session_id: str) -> str:
    """Return a compact, newline-joined sample of recent log lines for the
    session. Empty string when no logs are available — the agent should still
    be able to produce general questions in that case."""
    try:
        result = agent_tools.query_logs(
            session_id=session_id, query="", limit=LOG_SAMPLE_LIMIT
        )
    except Exception:
        logger.exception("query_logs failed during suggestion sampling")
        return ""
    lines: list[str] = []
    for entry in result.get("logs", []) or []:
        level = entry.get("level") or ""
        service = entry.get("service") or ""
        message = entry.get("raw_message") or ""
        prefix_bits = [b for b in (level, service) if b]
        prefix = f"[{' '.join(prefix_bits)}]" if prefix_bits else ""
        line = f"{prefix} {message}".strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def _run_agent(session_id: str) -> list[str]:
    """Build a small agent and ask it for three questions about the sample."""
    sample = _fetch_log_sample(session_id)
    if not sample.strip():
        sample = "(no logs available — produce three general framing questions)"

    agent: Agent[None, SuggestedQuestions] = Agent(
        _build_model(),
        output_type=SuggestedQuestions,
        instructions=SUGGESTION_INSTRUCTIONS,
        model_settings={"temperature": 0.3},
    )
    user_prompt = (
        "Log sample from this session:\n"
        "---\n"
        f"{sample}\n"
        "---\n"
        f"Return exactly {SUGGESTION_COUNT} questions."
    )
    result = agent.run_sync(user_prompt)
    return [q.strip() for q in result.output.questions if q.strip()]


def get_suggestions(session_id: str) -> list[str]:
    """Return three cached or freshly computed questions for the session.

    Returns ``[]`` if LLM is unconfigured or the agent run fails — the caller
    (the API endpoint) is expected to surface that to the UI as "no
    suggestions" rather than a hard error.
    """
    if not config.LLM_API_KEY:
        return []

    cached = _cache.get(session_id)
    if cached is not None:
        return cached

    lock = _get_session_lock(session_id)
    with lock:
        # Re-check under lock — another caller may have populated while we waited.
        cached = _cache.get(session_id)
        if cached is not None:
            return cached
        try:
            questions = _run_agent(session_id)
        except Exception:
            logger.exception(
                "suggestion agent failed for session_id=%s", session_id
            )
            return []
        _cache[session_id] = questions
        return questions


def invalidate(session_id: str) -> None:
    """Drop any cached suggestions for the session.

    Not called from anywhere today (uploads are second-rejected), but exposed
    so future flows (re-ingest, log delete) can keep the cache honest.
    """
    _cache.pop(session_id, None)


def _reset_cache_for_tests() -> dict[str, Any]:
    """Test-only helper to wipe state between cases."""
    _cache.clear()
    return _cache
