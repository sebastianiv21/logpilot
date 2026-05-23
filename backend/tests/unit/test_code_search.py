"""Unit tests for code_search: ripgrep-backed grep_repo and allowlisted read_file."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app.services import code_search


def _has_ripgrep() -> bool:
    return shutil.which("rg") is not None


requires_rg = pytest.mark.skipif(not _has_ripgrep(), reason="ripgrep not installed")


@pytest.fixture
def code_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A temp dir wired up as the only KNOWLEDGE_CODE_SOURCES entry."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "alpha.py").write_text(
        "def handle_request():\n"
        "    raise KafkaTimeoutException('connection refused')\n"
        "\n"
        "def other():\n"
        "    return 42\n"
    )
    (tmp_path / "src" / "beta.ts").write_text(
        "// kafka client\n"
        "export function connect() {\n"
        "  throw new Error('KafkaTimeoutException');\n"
        "}\n"
    )
    monkeypatch.setenv("KNOWLEDGE_CODE_SOURCES", str(tmp_path))
    return tmp_path


class TestGrepRepo:
    @requires_rg
    def test_finds_literal_token_across_files(self, code_root: Path):
        hits = code_search.grep_repo("KafkaTimeoutException")
        paths = {h.path for h in hits}
        assert any("alpha.py" in p for p in paths)
        assert any("beta.ts" in p for p in paths)

    @requires_rg
    def test_glob_restricts_to_extension(self, code_root: Path):
        hits = code_search.grep_repo("KafkaTimeoutException", glob="*.py")
        assert hits
        assert all(h.path.endswith(".py") for h in hits)

    @requires_rg
    def test_empty_pattern_returns_empty(self, code_root: Path):
        assert code_search.grep_repo("   ") == []

    @requires_rg
    def test_no_matches_returns_empty(self, code_root: Path):
        assert code_search.grep_repo("def_definitely_not_in_code_xyz123") == []

    def test_no_roots_configured_returns_empty(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("KNOWLEDGE_CODE_SOURCES", "")
        assert code_search.grep_repo("anything") == []

    @requires_rg
    def test_context_lines_captured(self, code_root: Path):
        hits = code_search.grep_repo(
            "KafkaTimeoutException", glob="*.py", context_lines=1
        )
        assert hits
        first = hits[0]
        # "raise KafkaTimeout..." has a line before it (the def line)
        assert any("def handle_request" in line for line in first.before)


class TestReadFile:
    def test_reads_slice_by_line_range(self, code_root: Path):
        path = "src/alpha.py"
        slice_ = code_search.read_file(path, line_start=1, line_end=2)
        assert slice_.path.endswith("alpha.py")
        assert slice_.line_start == 1
        assert slice_.line_end == 2
        assert "handle_request" in slice_.content
        assert "KafkaTimeoutException" in slice_.content
        assert "other" not in slice_.content
        assert slice_.total_lines >= 5
        assert slice_.truncated is False

    def test_reads_full_file_when_no_end_given(self, code_root: Path):
        slice_ = code_search.read_file("src/alpha.py")
        assert "handle_request" in slice_.content
        assert "other" in slice_.content

    def test_accepts_absolute_path_under_root(self, code_root: Path):
        abs_path = str(code_root / "src" / "alpha.py")
        slice_ = code_search.read_file(abs_path, line_start=1, line_end=1)
        assert "handle_request" in slice_.content

    def test_outside_allowlist_raises(
        self, code_root: Path, tmp_path_factory: pytest.TempPathFactory
    ):
        outside = tmp_path_factory.mktemp("outside") / "evil.py"
        outside.write_text("nope")
        with pytest.raises(code_search.OutsideAllowlistError):
            code_search.read_file(str(outside))

    def test_traversal_escape_raises(self, code_root: Path):
        with pytest.raises(code_search.OutsideAllowlistError):
            code_search.read_file("src/../../../etc/passwd")

    def test_no_roots_configured_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("KNOWLEDGE_CODE_SOURCES", "")
        with pytest.raises(code_search.OutsideAllowlistError):
            code_search.read_file("anything.py")
