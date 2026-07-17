"""
Tests for ai_judge.py. The Anthropic client is always mocked here — these
tests never touch the network. Live-API tests (marked @pytest.mark.live) live
at the bottom and are excluded from default `pytest` runs (see pytest.ini).
"""
import json
import types
from unittest.mock import MagicMock

import pytest

import ai_judge


def make_fake_response(json_str: str):
    """Minimal stand-in for an Anthropic Message response — ai_judge only ever
    reads block.type / block.text off response.content, so a plain
    SimpleNamespace is enough; no need to depend on real SDK model classes."""
    return types.SimpleNamespace(
        content=[types.SimpleNamespace(type="text", text=json_str)]
    )


# --- get_client() ---

def test_get_client_returns_none_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert ai_judge.get_client() is None


def test_get_client_returns_client_with_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key-for-test")
    monkeypatch.setattr(ai_judge.anthropic, "Anthropic", lambda api_key: "fake-client-object")
    assert ai_judge.get_client() == "fake-client-object"


def test_get_client_caches_result(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key-for-test")
    call_count = {"n": 0}

    def fake_anthropic(api_key):
        call_count["n"] += 1
        return "fake-client-object"

    monkeypatch.setattr(ai_judge.anthropic, "Anthropic", fake_anthropic)
    ai_judge.get_client()
    ai_judge.get_client()
    assert call_count["n"] == 1


# --- judge_text(): missing key short-circuits before any API call ---

def test_judge_text_returns_none_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert ai_judge.judge_text("some post text", {}) is None


# --- judge_text(): mocked client, response parsing/validation ---

def _mock_client_returning(json_str):
    client = MagicMock()
    client.messages.create.return_value = make_fake_response(json_str)
    return client


@pytest.mark.parametrize("verdict_key,expected_emoji", [
    ("likely_human", "🟢 Likely Human"),
    ("uncertain", "🟡 Possibly AI-Generated"),
    ("likely_ai", "🔴 Potentially AI-Generated"),
])
def test_judge_text_maps_each_verdict_correctly(monkeypatch, verdict_key, expected_emoji):
    payload = json.dumps({"verdict": verdict_key, "confidence": 0.75, "reasoning": "test reasoning"})
    client = _mock_client_returning(payload)
    monkeypatch.setattr(ai_judge, "get_client", lambda: client)

    result = ai_judge.judge_text("some post text", {"perplexity": 12.3})

    assert result == {"verdict": expected_emoji, "confidence": 0.75, "reasoning": "test reasoning"}


def test_judge_text_passes_model_and_structured_output_config(monkeypatch):
    payload = json.dumps({"verdict": "likely_human", "confidence": 0.5, "reasoning": "x"})
    client = _mock_client_returning(payload)
    monkeypatch.setattr(ai_judge, "get_client", lambda: client)

    ai_judge.judge_text("some post text", {})

    _, kwargs = client.messages.create.call_args
    assert kwargs["model"] == "claude-sonnet-5"
    assert kwargs["output_config"] == {"format": {"type": "json_schema", "schema": ai_judge.SCHEMA}}


def test_judge_text_returns_none_on_api_exception(monkeypatch):
    client = MagicMock()
    client.messages.create.side_effect = Exception("network exploded")
    monkeypatch.setattr(ai_judge, "get_client", lambda: client)

    assert ai_judge.judge_text("some post text", {}) is None


def test_judge_text_returns_none_when_no_text_block(monkeypatch):
    client = MagicMock()
    import types
    client.messages.create.return_value = types.SimpleNamespace(
        content=[types.SimpleNamespace(type="thinking", text=None)]
    )
    monkeypatch.setattr(ai_judge, "get_client", lambda: client)

    assert ai_judge.judge_text("some post text", {}) is None


def test_judge_text_returns_none_on_unparsable_json(monkeypatch):
    client = _mock_client_returning("not valid json at all")
    monkeypatch.setattr(ai_judge, "get_client", lambda: client)

    assert ai_judge.judge_text("some post text", {}) is None


def test_judge_text_returns_none_on_unknown_verdict(monkeypatch):
    payload = json.dumps({"verdict": "maybe_kinda", "confidence": 0.5, "reasoning": "x"})
    client = _mock_client_returning(payload)
    monkeypatch.setattr(ai_judge, "get_client", lambda: client)

    assert ai_judge.judge_text("some post text", {}) is None


def test_judge_text_does_not_call_api_without_client(monkeypatch):
    monkeypatch.setattr(ai_judge, "get_client", lambda: None)
    # No mock to assert against here by design: get_client() returning None
    # means judge_text must short-circuit before touching .messages.create.
    result = ai_judge.judge_text("some post text", {})
    assert result is None


# --- live tests: real API calls, shape-only assertions ---

@pytest.mark.live
def test_live_judge_returns_valid_shape_for_human_text():
    result = ai_judge.judge_text(
        "I went to the store today and forgot my wallet, had to drive all the way back home. "
        "So annoying, wasted like 20 minutes for nothing.",
        {"word_count": 30},
    )
    assert result is not None
    assert result["verdict"] in ai_judge.VERDICT_MAP.values()
    assert isinstance(result["confidence"], (int, float))
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["reasoning"], str) and result["reasoning"]


@pytest.mark.live
def test_live_judge_returns_valid_shape_for_short_generic_text():
    result = ai_judge.judge_text(
        "It is important to note that this topic has many facets worth discussing "
        "in detail, and in conclusion there are several key takeaways to consider.",
        {"word_count": 30},
    )
    assert result is not None
    assert result["verdict"] in ai_judge.VERDICT_MAP.values()


@pytest.mark.live
def test_live_judge_handles_empty_heuristic_context():
    result = ai_judge.judge_text("Just a plain sentence to check the API responds correctly.", {})
    assert result is not None
    assert result["verdict"] in ai_judge.VERDICT_MAP.values()
