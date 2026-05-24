"""Suggested questions API: per-session question pills for the UI."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.lib.config import config
from app.lib.repositories import SessionRepository
from app.services import suggestions

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions", "suggestions"])
_session_repo = SessionRepository()


class SuggestedQuestionsResponse(BaseModel):
    """GET /sessions/{session_id}/suggested-questions."""

    questions: list[str] = Field(
        default_factory=list,
        description=(
            "Three suggested incident questions for this session. Empty when "
            "the LLM isn't configured or the agent run failed — the UI should "
            "treat empty as 'no suggestions' rather than an error."
        ),
    )


@router.get(
    "/{session_id}/suggested-questions",
    response_model=SuggestedQuestionsResponse,
)
def get_suggested_questions(session_id: str) -> SuggestedQuestionsResponse:
    """Return three suggested questions for the session, computed on first
    call and cached in-process. 404 if the session doesn't exist; never 5xx
    on LLM/agent failure — degrades to an empty list."""
    if _session_repo.get(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if not config.LLM_API_KEY:
        # Same shape as a successful empty response — UI can decide whether
        # to show a hint instead of suggestions.
        return SuggestedQuestionsResponse(questions=[])
    return SuggestedQuestionsResponse(
        questions=suggestions.get_suggestions(session_id)
    )
