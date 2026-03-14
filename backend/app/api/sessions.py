"""Sessions API: list, create, get, update."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.lib.repositories import SessionRepository

router = APIRouter(prefix="/sessions", tags=["sessions"])
_repo = SessionRepository()


class SessionCreateBody(BaseModel):
    name: str | None = None
    external_link: str | None = None


class SessionUpdateBody(BaseModel):
    name: str | None = None
    external_link: str | None = None


@router.get("")
def list_sessions() -> dict:
    """GET /sessions — list all sessions."""
    sessions = _repo.list_all()
    return {"sessions": [s.to_api() for s in sessions]}


@router.post("", status_code=201)
def create_session(body: SessionCreateBody | None = None) -> dict:
    """POST /sessions — create a session. Body: optional name, external_link."""
    body = body or SessionCreateBody()
    session = _repo.create(name=body.name, external_link=body.external_link)
    return session.to_api()


@router.get("/{session_id}")
def get_session(session_id: str) -> dict:
    """GET /sessions/{session_id} — get one session. 404 if not found."""
    session = _repo.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_api()


@router.patch("/{session_id}")
def update_session(session_id: str, body: SessionUpdateBody | None = None) -> dict:
    """PATCH /sessions/{session_id} — partial update (name, external_link). 404 if not found."""
    body = body or SessionUpdateBody()
    session = _repo.update(session_id, name=body.name, external_link=body.external_link)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_api()
