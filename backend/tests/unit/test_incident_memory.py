"""Unit tests for cross-session incident memory.

Covers fingerprint composition, index_report metadata shape, search filter
plumbing, and the graceful-degradation paths (embeddings unavailable / store
failure / current-session exclusion).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.lib.embeddings import EmbeddingsUnavailableError
from app.services import incident_memory
from app.services.incident_memory import (
    REPORT_DOCUMENT_TYPE,
    REPORT_SOURCE_KEY,
    PastIncident,
    build_fingerprint,
    build_fingerprint_from_markdown,
    index_existing_report_content,
    index_report,
    search_past_incidents,
)
from app.services.report_model import (
    EvidenceItem,
    IncidentReport,
    RecommendedFix,
)


def _sample_report(**overrides) -> IncidentReport:
    base = dict(
        incident_summary="Payments started returning 503 at 14:02.",
        possible_root_cause="Kafka quorum loss blocking publish.",
        uncertainty="Not determined.",
        supporting_evidence=[
            EvidenceItem(description="Loki shows 47 errors in 6 minutes.", source="logs"),
            EvidenceItem(description="error_rate jumped from 0.1% to 8%.", source="metrics"),
        ],
        recommended_fix=RecommendedFix(non_code_steps=["Restart payments."]),
        next_troubleshooting_steps=["Run `kubectl logs payments`."],
        coding_agent_fix_prompt="Investigate Kafka retry behavior.",
    )
    base.update(overrides)
    return IncidentReport(**base)


class TestFingerprint:
    def test_includes_summary_root_cause_evidence(self) -> None:
        fp = build_fingerprint(_sample_report())
        assert "Payments started returning 503" in fp
        assert "Kafka quorum loss" in fp
        assert "(logs)" in fp
        assert "(metrics)" in fp

    def test_excludes_recommended_fix_and_troubleshooting(self) -> None:
        fp = build_fingerprint(_sample_report())
        assert "Restart payments" not in fp
        assert "kubectl logs" not in fp
        assert "Investigate Kafka retry" not in fp

    def test_empty_evidence_still_produces_text(self) -> None:
        fp = build_fingerprint(_sample_report(supporting_evidence=[]))
        assert "Payments started returning 503" in fp
        assert "Kafka quorum loss" in fp


class TestFingerprintFromMarkdown:
    def test_extracts_only_summary_root_cause_evidence_sections(self) -> None:
        content = (
            "## Incident Summary\nA short summary.\n\n"
            "## Possible Root Cause\nThe root cause.\n\n"
            "## Uncertainty\nSome uncertainty.\n\n"
            "## Supporting Evidence\nThe evidence text.\n\n"
            "## Recommended Fix\nRestart everything.\n\n"
            "## Coding agent fix prompt\nDo the thing.\n"
        )
        fp = build_fingerprint_from_markdown(content)
        assert "A short summary." in fp
        assert "The root cause." in fp
        assert "The evidence text." in fp
        # Uncertainty / fix / coding prompt excluded
        assert "Some uncertainty" not in fp
        assert "Restart everything" not in fp
        assert "Do the thing" not in fp

    def test_skips_not_determined_sections(self) -> None:
        content = (
            "## Incident Summary\nA short summary.\n\n"
            "## Possible Root Cause\n*Not determined.*\n\n"
            "## Supporting Evidence\nReal evidence.\n"
        )
        fp = build_fingerprint_from_markdown(content)
        assert "A short summary." in fp
        assert "Real evidence." in fp
        assert "*Not determined.*" not in fp

    def test_empty_when_no_known_sections_present(self) -> None:
        assert build_fingerprint_from_markdown("just some random text") == ""


class TestIndexReport:
    def test_upserts_chunk_with_session_id_in_metadata(self) -> None:
        fake_store = MagicMock()
        report = _sample_report()
        with patch.object(incident_memory, "embed_text", return_value=[0.1, 0.2, 0.3]), \
             patch.object(incident_memory, "get_vector_store", return_value=fake_store):
            ok = index_report(
                session_id="sess-1",
                report_id="rep-1",
                question="Why are payments 503ing?",
                created_at="2026-05-23T14:00:00Z",
                report=report,
            )
        assert ok is True
        # Delete-then-upsert so re-runs are idempotent.
        fake_store.delete.assert_called_once_with(
            source_key=REPORT_SOURCE_KEY, source_path="reports/rep-1"
        )
        fake_store.upsert.assert_called_once()
        (chunks,) = fake_store.upsert.call_args.args
        assert len(chunks) == 1
        chunk = chunks[0]
        assert chunk["document_type"] == REPORT_DOCUMENT_TYPE
        assert chunk["source_key"] == REPORT_SOURCE_KEY
        assert chunk["embedding"] == [0.1, 0.2, 0.3]
        meta = chunk["metadata"]
        assert meta["session_id"] == "sess-1"
        assert meta["report_id"] == "rep-1"
        assert meta["question"] == "Why are payments 503ing?"
        assert meta["created_at"] == "2026-05-23T14:00:00Z"
        assert "Payments started returning 503" in meta["summary"]

    def test_returns_false_and_logs_when_embeddings_unavailable(self) -> None:
        fake_store = MagicMock()
        with patch.object(
            incident_memory, "embed_text",
            side_effect=EmbeddingsUnavailableError("LLM_API_KEY not set"),
        ), patch.object(incident_memory, "get_vector_store", return_value=fake_store):
            ok = index_report(
                session_id="sess-1",
                report_id="rep-1",
                question="Why?",
                created_at="t",
                report=_sample_report(),
            )
        assert ok is False
        fake_store.upsert.assert_not_called()

    def test_returns_false_when_store_upsert_fails(self) -> None:
        fake_store = MagicMock()
        fake_store.upsert.side_effect = RuntimeError("pg down")
        with patch.object(incident_memory, "embed_text", return_value=[0.0]), \
             patch.object(incident_memory, "get_vector_store", return_value=fake_store):
            ok = index_report(
                session_id="sess-1",
                report_id="rep-1",
                question="Why?",
                created_at="t",
                report=_sample_report(),
            )
        assert ok is False

    def test_empty_fingerprint_is_skipped(self) -> None:
        # IncidentReport requires non-empty scalars at the schema level — but a
        # report with whitespace-only summary/root_cause produces empty fingerprint.
        report = _sample_report(
            incident_summary="   ",
            possible_root_cause="   ",
            supporting_evidence=[],
        )
        fake_store = MagicMock()
        with patch.object(incident_memory, "embed_text") as embed, \
             patch.object(incident_memory, "get_vector_store", return_value=fake_store):
            ok = index_report(
                session_id="sess-1",
                report_id="rep-1",
                question="Why?",
                created_at="t",
                report=report,
            )
        assert ok is False
        embed.assert_not_called()
        fake_store.upsert.assert_not_called()


class TestIndexExistingReportContent:
    def test_indexes_from_rendered_markdown(self) -> None:
        content = (
            "## Incident Summary\nPayments 503 spike at 14:02.\n\n"
            "## Possible Root Cause\nKafka quorum loss.\n\n"
            "## Supporting Evidence\nLoki shows 47 errors.\n"
        )
        fake_store = MagicMock()
        with patch.object(incident_memory, "embed_text", return_value=[0.5]), \
             patch.object(incident_memory, "get_vector_store", return_value=fake_store):
            ok = index_existing_report_content(
                session_id="sess-1",
                report_id="rep-old",
                question="Why?",
                created_at="2024-01-01T00:00:00Z",
                content=content,
            )
        assert ok is True
        (chunks,) = fake_store.upsert.call_args.args
        meta = chunks[0]["metadata"]
        assert "Payments 503 spike" in meta["summary"]
        assert "Kafka quorum loss" in meta["root_cause"]


class TestSearchPastIncidents:
    def test_passes_exclude_session_id_filter(self) -> None:
        fake_store = MagicMock()
        fake_store.search.return_value = []
        with patch.object(incident_memory, "embed_text", return_value=[0.0]), \
             patch.object(incident_memory, "get_vector_store", return_value=fake_store):
            search_past_incidents("Kafka timeouts", current_session_id="sess-current")
        _, kwargs = fake_store.search.call_args
        assert kwargs["filters"]["exclude_session_id"] == "sess-current"
        assert kwargs["filters"]["document_type"] == REPORT_DOCUMENT_TYPE

    def test_filters_out_low_similarity_matches(self) -> None:
        fake_store = MagicMock()
        fake_store.search.return_value = [
            {
                "content": "x",
                "score": 0.8,
                "metadata": {
                    "session_id": "s-a",
                    "report_id": "r-a",
                    "question": "Q1",
                    "summary": "S1",
                    "root_cause": "RC1",
                    "created_at": "t",
                },
            },
            {
                "content": "x",
                "score": 0.5,  # below threshold
                "metadata": {
                    "session_id": "s-b",
                    "report_id": "r-b",
                    "question": "Q2",
                    "summary": "S2",
                    "root_cause": "RC2",
                    "created_at": "t",
                },
            },
        ]
        with patch.object(incident_memory, "embed_text", return_value=[0.0]), \
             patch.object(incident_memory, "get_vector_store", return_value=fake_store):
            results = search_past_incidents(
                "anything", current_session_id="sess-cur", min_similarity=0.75
            )
        assert len(results) == 1
        assert isinstance(results[0], PastIncident)
        assert results[0].session_id == "s-a"
        assert results[0].similarity == 0.8

    def test_empty_query_returns_empty_without_calling_embeddings(self) -> None:
        with patch.object(incident_memory, "embed_text") as embed:
            assert search_past_incidents("   ", current_session_id="sess-cur") == []
        embed.assert_not_called()

    def test_returns_empty_when_embeddings_unavailable(self) -> None:
        with patch.object(
            incident_memory, "embed_text",
            side_effect=EmbeddingsUnavailableError("LLM_API_KEY not set"),
        ):
            assert search_past_incidents("Q", current_session_id="sess-cur") == []

    def test_returns_empty_when_store_search_raises(self) -> None:
        fake_store = MagicMock()
        fake_store.search.side_effect = RuntimeError("pg down")
        with patch.object(incident_memory, "embed_text", return_value=[0.0]), \
             patch.object(incident_memory, "get_vector_store", return_value=fake_store):
            assert search_past_incidents("Q", current_session_id="sess-cur") == []
