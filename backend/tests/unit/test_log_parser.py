"""Tests for log_parser: Go timestamp pattern and multi-line folding."""
from __future__ import annotations

from app.services.log_parser import parse_line, parse_lines


class TestGoTimestampPattern:
    def test_go_default_log_format(self) -> None:
        line = "2026/03/13 12:44:49 Loading config; env=development-postgres"
        rec = parse_line(line)
        assert rec.structured is True
        assert "Loading config" in rec.message
        assert rec.timestamp_ns > 0

    def test_go_log_with_file_list(self) -> None:
        line = "2026/03/13 12:44:49 Loading config files=[/tmp/config.yaml]"
        rec = parse_line(line)
        assert rec.structured is True
        assert "Loading config files" in rec.message


class TestMultiLineFolding:
    def test_stack_trace_folds_into_preceding_record(self) -> None:
        lines = [
            "2026-03-13T12:45:00.000Z ERROR Something went wrong",
            "    at module.func (/src/app.ts:10:5)",
            "    at process.run (node:internal/main:95:3)",
        ]
        records, rejected = parse_lines(lines)
        assert len(records) == 1
        assert rejected == 0
        assert records[0].structured is True
        assert "at module.func" in records[0].raw_message
        assert "at process.run" in records[0].raw_message

    def test_java_caused_by_folds(self) -> None:
        lines = [
            "2026-03-13 12:45:43,119 ERROR [io.quarkus] NullPointerException",
            "Caused by: java.lang.NullPointerException: null",
            "    at com.example.Foo.bar(Foo.java:42)",
        ]
        records, rejected = parse_lines(lines)
        assert len(records) == 1
        assert rejected == 0
        assert "Caused by" in records[0].raw_message

    def test_closing_braces_fold(self) -> None:
        lines = [
            '2026-03-13T12:45:00.000Z ERROR connection error {',
            '  "host": "localhost",',
            '}',
        ]
        records, rejected = parse_lines(lines)
        assert len(records) == 1
        assert rejected == 0

    def test_plain_text_without_preceding_structured_stays_rejected(self) -> None:
        lines = [
            "mkdir: created directory '/some/path'",
            "Using Keycloak DB URL",
            "CREATE SCHEMA",
        ]
        records, rejected = parse_lines(lines)
        assert len(records) == 3
        assert rejected == 3

    def test_plain_text_after_structured_folds(self) -> None:
        lines = [
            "2026-03-13T12:44:47.191Z Load environment configuration",
            "mkdir: created directory '/appsmith-stacks/git-storage'",
            "Using Keycloak DB URL",
        ]
        records, rejected = parse_lines(lines)
        assert len(records) == 1
        assert rejected == 0
        assert "mkdir:" in records[0].raw_message

    def test_new_structured_entry_breaks_folding(self) -> None:
        lines = [
            "2026-03-13T12:45:00.000Z INFO first message",
            "    continuation line",
            "2026-03-13T12:45:01.000Z WARN second message",
        ]
        records, rejected = parse_lines(lines)
        assert len(records) == 2
        assert rejected == 0
        assert "continuation line" in records[0].raw_message
        assert records[1].message.strip() == "second message"

    def test_empty_lines_skipped(self) -> None:
        lines = [
            "2026-03-13T12:45:00.000Z INFO hello",
            "",
            "   ",
            "2026-03-13T12:45:01.000Z INFO world",
        ]
        records, rejected = parse_lines(lines)
        assert len(records) == 2
        assert rejected == 0

    def test_json_entry_starts_new_record(self) -> None:
        lines = [
            "2026-03-13T12:45:00.000Z INFO first",
            "    some continuation",
            '{"level": 30, "msg": "json entry", "time": 1741868700000}',
        ]
        records, rejected = parse_lines(lines)
        assert len(records) == 2
        assert records[0].structured is True
        assert records[1].structured is True
        assert "some continuation" in records[0].raw_message

    def test_unstructured_before_any_structured_are_rejected(self) -> None:
        lines = [
            "APPSMITH_GIT_ROOT: /appsmith-stacks/git-storage",
            "SLF4J(W): Class path contains multiple SLF4J providers.",
            "2026-03-13T12:45:00.000Z INFO first real entry",
        ]
        records, rejected = parse_lines(lines)
        assert len(records) == 3
        assert rejected == 2
        assert records[0].structured is False
        assert records[1].structured is False
        assert records[2].structured is True


class TestGoTimestampParsing:
    def test_slash_date_parsed_to_valid_nanoseconds(self) -> None:
        line = "2026/03/13 12:44:49 some message"
        rec = parse_line(line)
        assert rec.structured is True
        assert rec.timestamp_ns != 0
