import types

import pytest

import ai_judge


@pytest.fixture(autouse=True)
def reset_ai_judge_client_cache(monkeypatch):
    """ai_judge caches the Anthropic client in module globals so it's only
    constructed once. Reset that cache between tests so each test controls
    whether get_client() sees an API key, instead of leaking state from
    whichever test ran first."""
    monkeypatch.setattr(ai_judge, "_client", None)
    monkeypatch.setattr(ai_judge, "_client_checked", False)


def make_fake_response(json_str: str):
    """Builds a minimal stand-in for an Anthropic Message response. ai_judge
    only ever reads block.type / block.text off response.content, so a plain
    SimpleNamespace is enough — no need to depend on real SDK model classes."""
    return types.SimpleNamespace(
        content=[types.SimpleNamespace(type="text", text=json_str)]
    )
