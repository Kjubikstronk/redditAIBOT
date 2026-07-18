import types

import pytest

import ai_judge


@pytest.fixture(autouse=True)
def reset_ai_judge_client_cache(monkeypatch, tmp_path):
    """ai_judge caches the Anthropic client in module globals so it's only
    constructed once. Reset that cache between tests so each test controls
    whether get_client() sees an API key, instead of leaking state from
    whichever test ran first.

    Also redirects the budget guard's state file into pytest's tmp_path:
    several tests only mock get_client() and exercise the real
    get_budget_guard(), which would otherwise write a real
    .judge_budget_state.json into the project directory as a test side
    effect — and could even interact with a real bot's actual daily budget
    if the paths ever matched."""
    monkeypatch.setattr(ai_judge, "_client", None)
    monkeypatch.setattr(ai_judge, "_client_checked", False)
    monkeypatch.setattr(ai_judge, "_budget_guard", None)
    monkeypatch.setenv("JUDGE_BUDGET_STATE_PATH", str(tmp_path / "test_judge_budget_state.json"))


def make_fake_response(json_str: str):
    """Builds a minimal stand-in for an Anthropic Message response. ai_judge
    only ever reads block.type / block.text off response.content, so a plain
    SimpleNamespace is enough — no need to depend on real SDK model classes."""
    return types.SimpleNamespace(
        content=[types.SimpleNamespace(type="text", text=json_str)]
    )
