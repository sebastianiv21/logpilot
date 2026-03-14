"""Sessions API: list, create, get, update."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.lib.repositories import SessionRepository

router = APIRouter(prefix="/sessions", tags=["sessions"])
_repo = SessionRepository()


class SessionResponse(BaseModel):
    """Single session as returned by API."""

    id: str
    name: str | None
    external_link: str | None
    created_at: str
    updated_at: str


class SessionListResponse(BaseModel):
    """GET /sessions response."""

    sessions: list[SessionResponse]


class SessionCreateBody(BaseModel):
    name: str | None = None
    external_link: str | None = None


class SessionUpdateBody(BaseModel):
    name: str | None = None
    external_link: str | None = None


@router.get("", response_model=SessionListResponse)
def list_sessions() -> SessionListResponse:
    """GET /sessions — list all sessions."""
    sessions = _repo.list_all()
    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s.to_api()) for s in sessions]
    )


@router.post("", status_code=201, response_model=SessionResponse)
def create_session(body: SessionCreateBody | None = None) -> SessionResponse:
    """POST /sessions — create a session. Body: optional name, external_link."""
    body = body or SessionCreateBody()
    session = _repo.create(name=body.name, external_link=body.external_link)
    return SessionResponse.model_validate(session.to_api())


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str) -> SessionResponse:
    """GET /sessions/{session_id} — get one session. 404 if not found."""
    session = _repo.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.model_validate(session.to_api())


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(session_id: str, body: SessionUpdateBody | None = None) -> SessionResponse:
    """PATCH /sessions/{session_id} — partial update (name, external_link). 404 if not found."""
    body = body or SessionUpdateBody()
    session = _repo.update(session_id, name=body.name, external_link=body.external_link)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.model_validate(session.to_api())
