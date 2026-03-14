"""Contract tests for sessions API (list, create, get, update) per contracts/api.md."""
import re
import uuid

import pytest

# Import after patching so config uses test DATA_DIR
from app.api.app import app
from app.lib import config as app_config
from fastapi.testclient import TestClient


def _session_shape(data: dict) -> dict[str, type | tuple]:
    """Required keys and types for a session object (contract)."""
    return {
        "id": str,
        "name": (str, type(None)),
        "external_link": (str, type(None)),
        "created_at": str,
        "updated_at": str,
    }


def _assert_session_object(obj: dict) -> None:
    for key, typ in _session_shape(obj).items():
        assert key in obj, f"missing key {key}"
        if typ is str:
            assert isinstance(obj[key], str), f"{key} should be str"
        else:
            assert isinstance(obj[key], (str, type(None))), f"{key} should be str or null"
    # id must be UUID format
    uuid_re = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    assert re.match(uuid_re, obj["id"], re.I), "id must be UUID"
    # ISO8601-like for datetimes
    assert "T" in obj["created_at"] and "T" in obj["updated_at"], "ISO8601"


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Test client with isolated SQLite in tmp_path."""
    monkeypatch.setattr(app_config.config, "DATA_DIR", tmp_path)
    return TestClient(app)


def test_list_sessions_empty(client: TestClient) -> None:
    """GET /sessions returns 200 and sessions array (empty)."""
    r = client.get("/sessions")
    assert r.status_code == 200
    data = r.json()
    assert "sessions" in data
    assert isinstance(data["sessions"], list)
    assert data["sessions"] == []


def test_create_session_201(client: TestClient) -> None:
    """POST /sessions returns 201 with session (id, name, external_link, created_at, updated_at)."""
    r = client.post("/sessions", json={})
    assert r.status_code == 201
    data = r.json()
    _assert_session_object(data)
    assert data["name"] is None
    assert data["external_link"] is None


def test_create_session_with_body(client: TestClient) -> None:
    """POST /sessions with name and external_link returns 201 and echoes them."""
    r = client.post(
        "/sessions",
        json={"name": "my-ticket", "external_link": "https://example.com/ticket/1"},
    )
    assert r.status_code == 201
    data = r.json()
    _assert_session_object(data)
    assert data["name"] == "my-ticket"
    assert data["external_link"] == "https://example.com/ticket/1"


def test_list_sessions_identifies_each(client: TestClient) -> None:
    """List identifies each session by creation time and/or link; if name set, include it."""
    client.post("/sessions", json={"name": "a", "external_link": "https://a.com"})
    r = client.get("/sessions")
    assert r.status_code == 200
    sessions = r.json()["sessions"]
    assert len(sessions) == 1
    _assert_session_object(sessions[0])
    assert sessions[0]["name"] == "a"
    assert sessions[0]["external_link"] == "https://a.com"
    assert sessions[0]["created_at"] and sessions[0]["updated_at"]


def test_get_session_200(client: TestClient) -> None:
    """GET /sessions/{session_id} returns 200 and same shape as single session."""
    create = client.post("/sessions", json={"name": "get-me"})
    assert create.status_code == 201
    sid = create.json()["id"]
    r = client.get(f"/sessions/{sid}")
    assert r.status_code == 200
    data = r.json()
    _assert_session_object(data)
    assert data["id"] == sid
    assert data["name"] == "get-me"


def test_get_session_404(client: TestClient) -> None:
    """GET /sessions/{session_id} returns 404 if not found; body has detail."""
    r = client.get(f"/sessions/{uuid.uuid4()}")
    assert r.status_code == 404
    data = r.json()
    assert "detail" in data


def test_update_session_200(client: TestClient) -> None:
    """PATCH /sessions/{session_id} returns 200 and updated session object."""
    create = client.post("/sessions", json={"name": "old", "external_link": "https://old.com"})
    assert create.status_code == 201
    sid = create.json()["id"]
    r = client.patch(f"/sessions/{sid}", json={"name": "new"})
    assert r.status_code == 200
    data = r.json()
    _assert_session_object(data)
    assert data["name"] == "new"
    assert data["external_link"] == "https://old.com"


def test_update_session_404(client: TestClient) -> None:
    """PATCH /sessions/{session_id} returns 404 if not found; body has detail."""
    r = client.patch(f"/sessions/{uuid.uuid4()}", json={"name": "x"})
    assert r.status_code == 404
    data = r.json()
    assert "detail" in data


def test_error_response_has_detail(client: TestClient) -> None:
    """Errors return body with at least 'detail' (contract base)."""
    r = client.get("/sessions/not-a-uuid")
    assert r.status_code == 404
    assert "detail" in r.json()
