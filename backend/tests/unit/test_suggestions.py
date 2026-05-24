"""Unit tests for the suggestions service.

The agent call itself is mocked — we want to lock in the cache shape, the
log-sample plumbing, and the graceful-degradation paths, not exercise
PydanticAI's structured-output guarantees (those are covered by
``test_report_model.py``).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services import suggestions
from app.services.suggestions import SuggestedQuestions


@pytest.fixture(autouse=True)
def _reset_cache():
    suggestions._reset_cache_for_tests()
    yield
    suggestions._reset_cache_for_tests()


class TestGetSuggestions:
    def test_returns_empty_when_llm_api_key_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(suggestions.config, "LLM_API_KEY", "")
        assert suggestions.get_suggestions("sess-1") == []

    def test_runs_agent_and_caches_per_session(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(suggestions.config, "LLM_API_KEY", "test-key")
        with patch.object(
            suggestions, "_run_agent", return_value=["q1?", "q2?", "q3?"]
        ) as run:
            first = suggestions.get_suggestions("sess-1")
            second = suggestions.get_suggestions("sess-1")
        assert first == ["q1?", "q2?", "q3?"]
        assert second == first
        # Cached — agent run exactly once.
        assert run.call_count == 1

    def test_different_sessions_run_independently(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(suggestions.config, "LLM_API_KEY", "test-key")
        with patch.object(
            suggestions,
            "_run_agent",
            side_effect=[["a?", "b?", "c?"], ["x?", "y?", "z?"]],
        ) as run:
            assert suggestions.get_suggestions("sess-a") == ["a?", "b?", "c?"]
            assert suggestions.get_suggestions("sess-b") == ["x?", "y?", "z?"]
        assert run.call_count == 2

    def test_agent_failure_returns_empty_and_does_not_cache(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(suggestions.config, "LLM_API_KEY", "test-key")
        with patch.object(
            suggestions, "_run_agent", side_effect=RuntimeError("boom")
        ) as run:
            assert suggestions.get_suggestions("sess-1") == []
            # Subsequent call retries — failure is not poisoned into the cache.
            assert suggestions.get_suggestions("sess-1") == []
        assert run.call_count == 2

    def test_invalidate_drops_cached_entry(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(suggestions.config, "LLM_API_KEY", "test-key")
        with patch.object(
            suggestions, "_run_agent", return_value=["q1?", "q2?", "q3?"]
        ) as run:
            suggestions.get_suggestions("sess-1")
            suggestions.invalidate("sess-1")
            suggestions.get_suggestions("sess-1")
        assert run.call_count == 2


class TestLogSampling:
    def test_fetch_log_sample_formats_entries(self):
        fake_logs = {
            "logs": [
                {
                    "level": "ERROR",
                    "service": "payments",
                    "raw_message": "KafkaTimeoutException",
                },
                {
                    "level": "INFO",
                    "service": "payments",
                    "raw_message": "Retry attempt 1",
                },
            ]
        }
        with patch.object(suggestions.agent_tools, "query_logs", return_value=fake_logs):
            sample = suggestions._fetch_log_sample("sess-1")
        assert "[ERROR payments] KafkaTimeoutException" in sample
        assert "[INFO payments] Retry attempt 1" in sample
        # Newline-joined, one entry per line
        assert sample.count("\n") == 1

    def test_fetch_log_sample_returns_empty_when_loki_fails(self):
        with patch.object(
            suggestions.agent_tools, "query_logs", side_effect=RuntimeError("loki down")
        ):
            assert suggestions._fetch_log_sample("sess-1") == ""

    def test_fetch_log_sample_drops_empty_messages(self):
        fake_logs = {
            "logs": [
                {"level": "", "service": "", "raw_message": ""},
                {"level": "INFO", "service": "x", "raw_message": "real line"},
            ]
        }
        with patch.object(suggestions.agent_tools, "query_logs", return_value=fake_logs):
            sample = suggestions._fetch_log_sample("sess-1")
        assert sample == "[INFO x] real line"


class TestSuggestedQuestionsModel:
    def test_requires_exactly_three(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SuggestedQuestions(questions=["one?", "two?"])
        with pytest.raises(ValidationError):
            SuggestedQuestions(questions=["1?", "2?", "3?", "4?"])
        SuggestedQuestions(questions=["1?", "2?", "3?"])  # ok
