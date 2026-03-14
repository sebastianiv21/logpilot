"""Configurable LLM client (OpenAI base_url + api_key from config)."""

from __future__ import annotations

from openai import OpenAI

from app.lib.config import config


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client using config (LLM_BASE_URL, LLM_API_KEY)."""
    return OpenAI(
        api_key=config.LLM_API_KEY or "",
        base_url=config.LLM_BASE_URL or "https://api.openai.com/v1",
    )


def chat_completion(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    temperature: float = 0.2,
) -> str:
    """
    Call the configured LLM chat API; returns the assistant message content.
    Raises if LLM_API_KEY is not set or the API call fails.
    """
    if not config.LLM_API_KEY:
        raise ValueError("LLM_API_KEY not set")
    client = get_client()
    resp = client.chat.completions.create(
        model=model or config.LLM_MODEL,
        messages=messages,
        temperature=temperature,
    )
    choice = resp.choices[0] if resp.choices else None
    if choice is None:
        raise ValueError("Empty completion response")
    return (choice.message.content or "").strip()
