"""Unit tests for the Vector sidecar drop step in the upload pipeline.

Focused on the helper that copies files into the shared volume — the surface
that touches Vector. Full upload integration is covered by test_upload_api;
here we lock in the path layout, the failure-doesn't-break-upload contract,
and the sanitization that protects the volume from path traversal.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services import upload as upload_service


def _set_drop_root(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    monkeypatch.setattr(upload_service.config, "VECTOR_LOG_DROP_DIR", str(root))


class TestDropToVectorDir:
    def test_writes_file_under_session_service_layout(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        drop_root = tmp_path / "vector_drop"
        _set_drop_root(monkeypatch, drop_root)
        src = tmp_path / "src.log"
        src.write_text("hello\nworld\n")

        ok = upload_service._drop_to_vector_dir(
            src, session_id="sess-1", service="payments", filename="app.log"
        )

        assert ok is True
        target = drop_root / "sess-1" / "payments" / "app.log"
        assert target.exists()
        assert target.read_text() == "hello\nworld\n"

    def test_returns_false_when_drop_dir_not_configured(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(upload_service.config, "VECTOR_LOG_DROP_DIR", "")
        src = tmp_path / "src.log"
        src.write_text("x")
        assert (
            upload_service._drop_to_vector_dir(
                src, session_id="sess", service="svc", filename="a.log"
            )
            is False
        )

    def test_copy_failure_returns_false_without_raising(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        _set_drop_root(monkeypatch, tmp_path / "vector_drop")
        missing = tmp_path / "does-not-exist.log"
        # The source file doesn't exist — shutil.copyfile raises, helper catches.
        assert (
            upload_service._drop_to_vector_dir(
                missing, session_id="sess", service="svc", filename="a.log"
            )
            is False
        )

    def test_sanitizes_path_components_against_traversal(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        drop_root = tmp_path / "vector_drop"
        _set_drop_root(monkeypatch, drop_root)
        src = tmp_path / "src.log"
        src.write_text("x")

        ok = upload_service._drop_to_vector_dir(
            src,
            session_id="../escape",
            service="svc/with/slash",
            filename="../../../etc/passwd",
        )

        assert ok is True
        # Every part is sanitized; nothing lands outside drop_root.
        for path in drop_root.rglob("*"):
            assert drop_root in path.resolve().parents or path == drop_root
        # The escape attempts didn't create files in tmp_path's parent.
        assert not (tmp_path / "etc").exists()
        assert not (tmp_path.parent / "etc" / "passwd").exists()


class TestSafePathComponent:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("ordinary", "ordinary"),
            ("with-dash_and.dot", "with-dash_and.dot"),
            # Slash is replaced with _; leading dots are stripped after.
            ("../escape", "_escape"),
            ("svc/with/slash", "svc_with_slash"),
            ("trailing space ", "trailing_space_"),
            ("..hidden", "hidden"),
        ],
    )
    def test_replaces_unsafe_characters(self, raw: str, expected: str):
        assert upload_service._safe_path_component(raw, fallback="x") == expected

    def test_returns_fallback_for_empty_or_dot_only(self):
        assert upload_service._safe_path_component("", fallback="default") == "default"
        assert upload_service._safe_path_component("...", fallback="default") == "default"
