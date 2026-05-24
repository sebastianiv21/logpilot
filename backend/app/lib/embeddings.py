"""OpenAI-compatible text embedding helper.

Single place every service goes through to embed strings. Used by the
knowledge ingest pipeline and by incident-memory indexing/search.
"""

from __future__ import annotations

import logging

from openai import OpenAI

from app.lib.config import config

logger = logging.getLogger(__name__)

# Stay well under OpenAI's per-request input limit (8192 inputs); 50 is a
# conservative batch size that keeps latency reasonable for incremental work.
_BATCH_SIZE = 50


class EmbeddingsUnavailableError(RuntimeError):
    """Raised when LLM_API_KEY is unset and the caller asked to embed."""


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed every input string. Empty input returns an empty list.

    Raises :class:`EmbeddingsUnavailableError` if no API key is configured.
    Callers that should degrade gracefully (e.g. background indexing) are
    expected to catch this.
    """
    if not texts:
        return []
    if not config.LLM_API_KEY:
        raise EmbeddingsUnavailableError(
            "LLM_API_KEY (or OPENAI_API_KEY) required for embeddings"
        )
    client = OpenAI(
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL or "https://api.openai.com/v1",
    )
    out: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        resp = client.embeddings.create(input=batch, model=config.EMBEDDING_MODEL)
        out.extend(d.embedding for d in resp.data)
    return out


def embed_text(text: str) -> list[float]:
    """Embed a single string. Convenience wrapper around :func:`embed_texts`."""
    vectors = embed_texts([text])
    return vectors[0] if vectors else []
