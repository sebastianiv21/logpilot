"""Unit tests for knowledge service: chunking, document type, file collection."""
from pathlib import Path

import pytest

from app.services.knowledge import (
    DOCS_EXTENSIONS,
    KNOWN_EXTENSIONS,
    REPO_EXTENSIONS,
    _chunk_text,
    _collect_files,
    _document_type,
)


class TestChunkText:
    """Test fixed-size chunking with overlap."""

    def test_chunk_splits_by_size(self):
        text = "a" * 200
        chunks = _chunk_text(text, chunk_size=50, overlap=10)
        assert len(chunks) >= 3
        assert all(len(c) <= 50 for c in chunks)

    def test_chunk_overlap(self):
        text = "hello world " * 50
        chunks = _chunk_text(text, chunk_size=40, overlap=15)
        # Overlap means next start = end - 15, so chunks overlap
        assert len(chunks) >= 2

    def test_empty_string_returns_empty_list(self):
        assert _chunk_text("", chunk_size=100, overlap=20) == []
        assert _chunk_text("   \n  ", chunk_size=100, overlap=20) == []

    def test_single_short_chunk(self):
        text = "short"
        assert _chunk_text(text, chunk_size=100, overlap=0) == ["short"]


class TestDocumentType:
    """Test document_type derivation from file extension."""

    @pytest.mark.parametrize("ext", [".md", ".mdx", ".mdc", ".markdown"])
    def test_markdown_extensions(self, ext):
        assert _document_type(Path(f"file{ext}")) == "markdown"

    def test_rst_is_rst(self):
        assert _document_type(Path("readme.rst")) == "rst"

    @pytest.mark.parametrize("ext", [".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".sql", ".json"])
    def test_source_extensions(self, ext):
        assert _document_type(Path(f"src{ext}")) == "source"

    @pytest.mark.parametrize("ext", [".yml", ".yaml", ".cfg", ".conf", ".ini", ".properties"])
    def test_config_extensions(self, ext):
        assert _document_type(Path(f"config{ext}")) == "config"

    def test_text_fallback(self):
        assert _document_type(Path("readme.txt")) == "text"
        assert _document_type(Path("doc.svg")) == "text"


class TestFileExtensions:
    """Test repo vs docs extension sets."""

    def test_repo_and_docs_defined(self):
        assert len(REPO_EXTENSIONS) >= 20
        assert len(DOCS_EXTENSIONS) >= 10

    def test_known_is_union(self):
        assert KNOWN_EXTENSIONS == REPO_EXTENSIONS | DOCS_EXTENSIONS

    def test_common_repo_extensions_included(self):
        assert ".ts" in REPO_EXTENSIONS
        assert ".tsx" in REPO_EXTENSIONS
        assert ".py" in REPO_EXTENSIONS
        assert ".md" in REPO_EXTENSIONS

    def test_docs_specific_included(self):
        assert ".txt" in DOCS_EXTENSIONS
        assert ".ini" in DOCS_EXTENSIONS
        assert ".svg" in DOCS_EXTENSIONS


class TestCollectFiles:
    """Test file discovery under source paths."""

    def test_collects_matching_extensions(self, tmp_path):
        (tmp_path / "readme.md").write_text("# Doc")
        (tmp_path / "script.py").write_text("print(1)")
        (tmp_path / "notes.txt").write_text("notes")
        (tmp_path / "binary.foo").write_bytes(b"\x00\x01")
        found = _collect_files([tmp_path])
        exts = {p.suffix.lower() for p in found}
        assert ".md" in exts
        assert ".py" in exts
        assert ".txt" in exts
        assert ".foo" not in exts
        assert len(found) == 3

    def test_single_file_source(self, tmp_path):
        md_file = tmp_path / "one.md"
        md_file.write_text("# One")
        found = _collect_files([md_file])
        assert len(found) == 1
        assert found[0].name == "one.md"

    def test_nonexistent_path_skipped(self, tmp_path):
        (tmp_path / "a.md").write_text("a")
        found = _collect_files([tmp_path, tmp_path / "missing"])
        assert len(found) == 1
